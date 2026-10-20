from fastapi import FastAPI, HTTPException, Query

import queries

app = FastAPI(title="UK Job Market Skills Radar API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/skills/trending")
def get_trending_skills(limit: int = Query(20, ge=1, le=100)):
    return queries.trending_skills(limit)


@app.get("/skills/trend")
def get_skill_trend(name: str = Query(..., min_length=1)):
    result = queries.skill_trend(name)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Skill '{name}' not found")
    return result


@app.get("/postings/latest")
def get_latest_postings(limit: int = Query(10, ge=1, le=100)):
    return queries.latest_postings(limit)