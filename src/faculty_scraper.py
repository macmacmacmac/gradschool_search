import requests
import csv
import time
import argparse
from institutions import EUROPEAN_COUNTRIES, get_prestige_score

def fetch_papers(query, max_papers=100):
    papers = []
    per_page = 50
    pages = (max_papers // per_page) + 1
    
    for page in range(1, pages + 1):
        url = "https://api.openalex.org/works"
        params = {
            "filter": f"title.search:{query}",
            "sort": "cited_by_count:desc",
            "per-page": per_page,
            "page": page
        }
        print(f"Fetching page {page} from OpenAlex...")
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            if not results:
                break
            papers.extend(results)
        else:
            print(f"Error fetching data: {response.status_code}")
            break
            
        time.sleep(0.5) # Polite delay
        
        if len(papers) >= max_papers:
            break
            
    return papers[:max_papers]

def process_faculty(papers):
    faculty = {}
    
    for paper in papers:
        title = paper.get("title", "Unknown Title")
        authorships = paper.get("authorships", [])
        
        for authorship in authorships:
            author = authorship.get("author", {})
            author_id = author.get("id")
            author_name = author.get("display_name")
            
            if not author_name or not author_id:
                continue
                
            # Usually we want PI / Faculty. In CS, they are often last authors. 
            # But let's just collect all authors and we can let the user filter, 
            # or we prioritize last authors. For now, we collect all.
            is_last = authorship.get("author_position") == "last"
            
            institutions = authorship.get("institutions", [])
            countries = authorship.get("countries", [])
            
            if not institutions:
                continue
                
            institution = institutions[0].get("display_name", "")
            
            # Check if any of the author's countries are in our target European list
            is_eu = any(country in EUROPEAN_COUNTRIES for country in countries)
            
            if is_eu:
                if author_id not in faculty:
                    prestige = get_prestige_score(institution)
                    faculty[author_id] = {
                        "Name": author_name,
                        "Institution": institution,
                        "Country": ", ".join(countries),
                        "Prestige_Tier": prestige,
                        "Profile_Link": author_id,
                        "Papers_Found": 1,
                        "Example_Paper": title,
                        "Likely_PI": is_last # If they were last author on at least one paper
                    }
                else:
                    faculty[author_id]["Papers_Found"] += 1
                    if is_last:
                        faculty[author_id]["Likely_PI"] = True
                        
    return list(faculty.values())

def main():
    parser = argparse.ArgumentParser(description="Scrape faculty for PhD outreach")
    parser.add_argument("--query", default='"mechanistic interpretability"', help="Search query")
    parser.add_argument("--max-papers", type=int, default=200, help="Max papers to fetch")
    parser.add_argument("--output", default="faculty_outreach.csv", help="Output CSV filename")
    
    args = parser.parse_args()
    
    print(f"Searching for papers matching: {args.query}")
    papers = fetch_papers(args.query, max_papers=args.max_papers)
    print(f"Found {len(papers)} papers. Processing authors...")
    
    faculty_list = process_faculty(papers)
    print(f"Found {len(faculty_list)} researchers in target regions.")
    
    # Sort by Prestige Tier (1 is best), then by Likely_PI, then by Papers Found
    faculty_list.sort(key=lambda x: (x["Prestige_Tier"], not x["Likely_PI"], -x["Papers_Found"]))
    
    if faculty_list:
        keys = ["Name", "Institution", "Country", "Prestige_Tier", "Likely_PI", "Papers_Found", "Example_Paper", "Profile_Link", "Email_Guess"]
        
        with open(args.output, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            for row in faculty_list:
                # Add empty email guess column for manual entry
                row["Email_Guess"] = ""
                writer.writerow(row)
                
        print(f"Successfully wrote {len(faculty_list)} researchers to {args.output}")
    else:
        print("No researchers found matching the criteria.")

if __name__ == "__main__":
    main()
