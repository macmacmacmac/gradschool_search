import sqlite3
import requests
import time
import logging
from config import KEYWORDS, TARGET_COUNTRY_CODES, DB_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            openalex_id TEXT PRIMARY KEY,
            title TEXT,
            abstract TEXT,
            doi TEXT,
            publication_year INTEGER,
            sent BOOLEAN DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS authors (
            openalex_id TEXT PRIMARY KEY,
            display_name TEXT,
            last_known_institution TEXT,
            country_code TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS paper_authors (
            paper_id TEXT,
            author_id TEXT,
            author_position TEXT,
            is_corresponding BOOLEAN,
            PRIMARY KEY (paper_id, author_id)
        )
    ''')
    conn.commit()
    return conn

def reconstruct_abstract(inverted_index):
    if not inverted_index:
        return "No abstract available."
    try:
        max_pos = max(pos for positions in inverted_index.values() for pos in positions)
        words = [""] * (max_pos + 1)
        for word, positions in inverted_index.items():
            for pos in positions:
                words[pos] = word
        return " ".join(words)
    except Exception:
        return "Abstract format error."

def fetch_works_for_keyword(keyword):
    works = []
    base_url = "https://api.openalex.org/works"
    # Search title, abstract, and full text for the exact phrase
    params = {
        "search": f'"{keyword}"',
        "filter": "concepts.id:C41008148",
        "per-page": 100,
        "cursor": "*"
    }
    
    logging.info(f"Fetching works for keyword: {keyword}")
    while params["cursor"]:
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            logging.error(f"Error fetching data: {response.status_code}")
            break
            
        data = response.json()
        results = data.get("results", [])
        if not results:
            break
            
        works.extend(results)
        params["cursor"] = data.get("meta", {}).get("next_cursor")
        time.sleep(0.1) # Be polite to API
        
    logging.info(f"Found {len(works)} works for '{keyword}'")
    return works

def process_works(works, conn):
    c = conn.cursor()
    new_papers_count = 0
    
    for work in works:
        work_id = work.get("id")
        if not work_id:
            continue
            
        # Check if we already have it
        c.execute("SELECT openalex_id FROM papers WHERE openalex_id = ?", (work_id,))
        if c.fetchone():
            continue
            
        authorships = work.get("authorships", [])
        
        # Check if ANY author is in Target Countries
        is_target = False
        
        for authorship in authorships:
            institutions = authorship.get("institutions", [])
            for inst in institutions:
                country_code = inst.get("country_code")
                if country_code and country_code.upper() in TARGET_COUNTRY_CODES:
                    is_target = True
                    break
        
        if not is_target:
            continue
            
        # It's a Target paper! Let's save it.
        title = work.get("title", "Untitled")
        abstract = reconstruct_abstract(work.get("abstract_inverted_index"))
        doi = work.get("doi", "")
        year = work.get("publication_year", 0)
        
        try:
            c.execute('''
                INSERT INTO papers (openalex_id, title, abstract, doi, publication_year)
                VALUES (?, ?, ?, ?, ?)
            ''', (work_id, title, abstract, doi, year))
            
            # Save authors
            for authorship in authorships:
                author = authorship.get("author", {})
                author_id = author.get("id")
                
                if not author_id:
                    continue
                    
                display_name = author.get("display_name", "Unknown")
                
                # Determine primary institution and country
                inst_name = "Unknown"
                country = None
                institutions = authorship.get("institutions", [])
                if institutions:
                    inst_name = institutions[0].get("display_name", "Unknown")
                    country = institutions[0].get("country_code")
                
                # Insert or ignore author (we might have seen them before)
                c.execute('''
                    INSERT OR IGNORE INTO authors (openalex_id, display_name, last_known_institution, country_code)
                    VALUES (?, ?, ?, ?)
                ''', (author_id, display_name, inst_name, country))
                
                # Save relationship
                position = authorship.get("author_position", "middle")
                is_corresp = authorship.get("is_corresponding", False)
                
                c.execute('''
                    INSERT OR IGNORE INTO paper_authors (paper_id, author_id, author_position, is_corresponding)
                    VALUES (?, ?, ?, ?)
                ''', (work_id, author_id, position, is_corresp))
            
            new_papers_count += 1
        except sqlite3.Error as e:
            logging.error(f"DB Error inserting paper {work_id}: {e}")
            
    conn.commit()
    return new_papers_count

def main():
    conn = init_db()
    total_added = 0
    
    for kw in KEYWORDS:
        works = fetch_works_for_keyword(kw)
        added = process_works(works, conn)
        total_added += added
        
    logging.info(f"Database build complete. Added {total_added} new Target region papers.")
    conn.close()

if __name__ == "__main__":
    main()
