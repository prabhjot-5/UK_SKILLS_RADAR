import spacy
from spacy.matcher import PhraseMatcher
from db import init_db

nlp = spacy.load("en_core_web_sm")

SKILLS = [
    "python", "sql", "java", "javascript", "typescript", "c++", "c#", "r",
    "react", "angular", "vue", "node.js", "django", "flask", "fastapi",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
    "git", "ci/cd", "jenkins", "linux",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "spacy", "nlp", "machine learning", "deep learning", "data analysis",
    "sqlite", "postgresql", "mongodb", "mysql",
    "streamlit", "plotly", "tableau", "power bi", "excel",
    "spark", "pyspark", "databricks", "snowflake", "airflow", "dbt",
    "llm", "mlops", "etl", "statistics",
    "agile", "scrum", "rest api", "graphql"
]

matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
for skill in SKILLS:
    matcher.add(skill, [nlp.make_doc(skill)])

def extract_skills(text):
    if not text:
        return []
    doc = nlp.make_doc(text)
    return sorted({nlp.vocab.strings[match_id] for match_id, start, end in matcher(doc)})

def process_postings(conn):
    c=conn.cursor()
    c.execute("DELETE FROM posting_skills")
    c.execute("DELETE FROM skills")
    c.execute("SELECT id, description FROM postings")
    postings =c.fetchall()

    skill_count=0
    for posting_id, description in postings:
        found_skills=extract_skills(description)
        for skill in found_skills:
            c.execute("INSERT OR IGNORE INTO skills (name) VALUES (?)", (skill,))
            c.execute("SELECT id FROM skills WHERE name = ?", (skill,))
            skill_id = c.fetchone()[0]
            c.execute("INSERT OR IGNORE INTO posting_skills (posting_id, skill_id) VALUES (?, ?)",
                       (posting_id, skill_id))
            skill_count += 1

    conn.commit()
    return len(postings), skill_count

if __name__ == "__main__":
    conn = init_db()
    total_postings, total_links = process_postings(conn)
    print(f"Processed {total_postings} postings, created {total_links} skill links.")
    conn.close()
            