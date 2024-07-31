from fastapi import FastAPI, Query
from src.athena import scrape_jobs
from pydantic import BaseModel
from typing import List

app = FastAPI()

class JobSearchParams(BaseModel):
    site_name: List[str] = Query(None)
    search_term: str = None
    location: str = None
    # Add other parameters as needed

@app.get("/api/jobs")
def get_jobs(params: JobSearchParams):
    jobs_df = scrape_jobs(
        site_name=params.site_name,
        search_term=params.search_term,
        location=params.location,
        # Pass other parameters
    )
    return jobs_df.to_dict(orient='records')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
