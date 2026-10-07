import os
import requests
from dotenv import load_dotenv
from db import init_db

load_dotenv()

def fetch_postings(pages=1, query="software engineer"):
    all_jobs = []
    for page in range(1, pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/gb/search/{page}"
        params = {
            "app_id": os.getenv("ADZUNA_APP_ID"),
            "app_key": os.getenv("ADZUNA_APP_KEY"),
            "what": query,
            "results_per_page": 50
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        all_jobs.extend(data.get("results", []))
    return all_jobs

def store_postings(jobs, conn):
    c = conn.cursor()
    inserted = 0
    for job in jobs:
        c.execute("""INSERT OR IGNORE INTO postings
            (adzuna_id, title, company, location, description, date_posted, url, salary_min, salary_max, category)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                job.get("id"),
                job.get("title"),
                job.get("company", {}).get("display_name"),
                job.get("location", {}).get("display_name"),
                job.get("description"),
                job.get("created"),
                job.get("redirect_url"),
                job.get("salary_min"),
                job.get("salary_max"),
                job.get("category", {}).get("label")
            )
        )
        if c.rowcount > 0:
            inserted += 1
    conn.commit()
    return inserted

if __name__ == "__main__":
    conn = init_db()
    jobs = fetch_postings(pages=2, query="software engineer")
    inserted = store_postings(jobs, conn)
    print(f"Fetched {len(jobs)} postings, inserted {inserted} new rows.")
    conn.close()        