import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "skills_radar.db"


def get_conn():
    conn = sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def trending_skills(limit=20):
    conn = get_conn()
    try:
        total = conn.execute("SELECT COUNT(*) FROM postings").fetchone()[0]
        rows = conn.execute(
            """SELECT s.name AS skill, COUNT(*) AS postings
               FROM posting_skills ps
               JOIN skills s ON s.id = ps.skill_id
               GROUP BY s.name
               ORDER BY postings DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
    finally:
        conn.close()
    return [
        {
            "skill": r["skill"],
            "postings": r["postings"],
            "share_pct": round(100 * r["postings"] / total, 1) if total else 0,
        }
        for r in rows
    ]


def latest_postings(limit=10):
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT p.id, p.title, p.company, p.location, p.date_posted, p.url,
                      GROUP_CONCAT(s.name) AS skills
               FROM postings p
               LEFT JOIN posting_skills ps ON ps.posting_id = p.id
               LEFT JOIN skills s ON s.id = ps.skill_id
               GROUP BY p.id
               ORDER BY p.date_posted DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
    finally:
        conn.close()
    results = []
    for r in rows:
        item = dict(r)
        item["skills"] = item["skills"].split(",") if item["skills"] else []
        results.append(item)
    return results


def skill_trend(skill):
    conn = get_conn()
    try:
        exists = conn.execute(
            "SELECT 1 FROM skills WHERE name = ?", (skill.lower(),)
        ).fetchone()
        if not exists:
            return None
        rows = conn.execute(
            """SELECT SUBSTR(p.date_posted, 1, 10) AS day,
                      COUNT(*) AS postings,
                      SUM(CASE WHEN EXISTS (
                          SELECT 1 FROM posting_skills ps
                          JOIN skills s ON s.id = ps.skill_id
                          WHERE ps.posting_id = p.id AND s.name = ?
                      ) THEN 1 ELSE 0 END) AS mentions
               FROM postings p
               GROUP BY day
               ORDER BY day""",
            (skill.lower(),),
        ).fetchall()
    finally:
        conn.close()
    return [
        {
            "day": r["day"],
            "postings": r["postings"],
            "mentions": r["mentions"],
            "share_pct": round(100 * r["mentions"] / r["postings"], 1),
        }
        for r in rows
    ]

def get_totals():
    conn = get_conn()
    try:
        postings = conn.execute("SELECT COUNT(*) FROM postings").fetchone()[0]
        links = conn.execute("SELECT COUNT(*) FROM posting_skills").fetchone()[0]
        skills = conn.execute(
            "SELECT COUNT(DISTINCT skill_id) FROM posting_skills"
        ).fetchone()[0]
    finally:
        conn.close()
    return {"postings": postings, "links": links, "skills": skills}


def all_skill_names():
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT s.name
               FROM skills s
               JOIN posting_skills ps ON ps.skill_id = s.id
               GROUP BY s.name
               ORDER BY COUNT(*) DESC"""
        ).fetchall()
    finally:
        conn.close()
    return [row["name"] for row in rows]