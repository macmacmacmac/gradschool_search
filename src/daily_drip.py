import sqlite3
import logging
from config import DB_PATH, EUROPEAN_COUNTRY_CODES
from email_sender import send_daily_email

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_candidate_pis_for_paper(conn, paper_id):
    c = conn.cursor()
    # Find all authors for this paper who are European
    c.execute('''
        SELECT a.openalex_id, a.display_name, a.last_known_institution, a.country_code, pa.author_position
        FROM authors a
        JOIN paper_authors pa ON a.openalex_id = pa.author_id
        WHERE pa.paper_id = ?
    ''', (paper_id,))
    authors = c.fetchall()
    
    pis = []
    for a in authors:
        if a['country_code'] and a['country_code'].upper() in EUROPEAN_COUNTRY_CODES:
            # Check how many papers this author has in our DB
            c.execute('SELECT COUNT(*) FROM paper_authors WHERE author_id = ?', (a['openalex_id'],))
            count = c.fetchone()[0]
            
            # Heuristic for PI: Last author OR has multiple papers in DB
            if a['author_position'] == 'last' or count > 1:
                pis.append({
                    'openalex_id': a['openalex_id'],
                    'display_name': a['display_name'],
                    'institution': a['last_known_institution'],
                    'country': a['country_code'],
                    'paper_count': count
                })
    return pis

def main():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Select 3 unseen papers that have AT LEAST ONE European PI
    # To do this, we'll fetch a batch of unsent papers and evaluate them
    # until we find 3 good ones.
    
    c.execute('SELECT * FROM papers WHERE sent = 0 ORDER BY RANDOM() LIMIT 50')
    unsent_papers = c.fetchall()
    
    selected_items = []
    
    for paper in unsent_papers:
        pis = get_candidate_pis_for_paper(conn, paper['openalex_id'])
        if pis:
            selected_items.append({
                'paper': dict(paper),
                'pis': pis
            })
            if len(selected_items) == 3:
                break
                
    if not selected_items:
        logging.info("No unsent papers found with matching PIs.")
        conn.close()
        return

    # Send Email
    success = send_daily_email(selected_items)
    
    # Mark as sent
    if success:
        for item in selected_items:
            c.execute('UPDATE papers SET sent = 1 WHERE openalex_id = ?', (item['paper']['openalex_id'],))
        conn.commit()
        logging.info(f"Marked {len(selected_items)} papers as sent.")
    
    conn.close()

if __name__ == "__main__":
    main()
