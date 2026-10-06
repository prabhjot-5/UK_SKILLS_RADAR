import sqlite3

def init_db(path="skills_radar.db"):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS postings (
        id INTEGER PRIMARY KEY,
        adzuna_id TEXT UNIQUE,
        title TEXT,
        company TEXT,
        location TEXT,
        description TEXT,
        date_posted TEXT,
        url TEXT,
        salary_min REAL,
        salary_max REAL,
        category TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS posting_skills (
        posting_id INTEGER,
        skill_id INTEGER,
        FOREIGN KEY(posting_id) REFERENCES postings(id),
        FOREIGN KEY(skill_id) REFERENCES skills(id)
    )""")

    conn.commit()
    return conn

if __name__ == "__main__":
    conn = init_db()
    print("Database initialized successfully.")
    conn.close()