from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import json
from apscheduler.schedulers.background import BackgroundScheduler
from src.athena import scrape_jobs, export_jobs_to_json  # Adjusted to absolute import
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE_MB = 1024  # Set maximum file size to 1GB

def generate_jobs_json(
    site_name=None,
    search_term=None,
    location=None,
    distance=50,
    is_remote=False,
    job_type=None,
    easy_apply=None,
    results_wanted=15,
    country_indeed="usa",
    description_format="markdown",
    linkedin_fetch_description=False,
    linkedin_company_ids=None,
    offset=0,
    hours_old=None,
    enforce_annual_salary=False,
    verbose=2,
    proxies=None,
):
    logger.info("Starting job scraping...")
    try:
        jobs = []
        total_size_mb = 0
        
        # Scrape jobs in chunks to monitor size
        while total_size_mb < MAX_FILE_SIZE_MB:
            df = scrape_jobs(
                site_name=site_name,
                search_term=search_term,
                location=location,
                distance=distance,
                is_remote=is_remote,
                job_type=job_type,
                easy_apply=easy_apply,
                results_wanted=results_wanted,
                country_indeed=country_indeed,
                description_format=description_format,
                linkedin_fetch_description=linkedin_fetch_description,
                linkedin_company_ids=linkedin_company_ids,
                offset=offset,
                hours_old=hours_old,
                enforce_annual_salary=enforce_annual_salary,
                verbose=verbose,
                proxies=proxies,
            )
            
            new_jobs = df.to_dict(orient='records')
            new_jobs_json_str = json.dumps(new_jobs, indent=4)
            new_jobs_size_mb = len(new_jobs_json_str.encode('utf-8')) / (1024 * 1024)
            
            if total_size_mb + new_jobs_size_mb > MAX_FILE_SIZE_MB:
                logger.info("Reached maximum file size limit. Stopping scraping.")
                break
            
            jobs.extend(new_jobs)
            total_size_mb += new_jobs_size_mb
            
            # Increment offset to avoid scraping the same jobs
            offset += results_wanted
            
        # Write to jobs.json
        with open("jobs.json", "w") as f:
            json.dump(jobs, f, indent=4)
        logger.info("jobs.json file created successfully.")
        
        # Commented truncation code for future use
        # if total_size_mb > MAX_FILE_SIZE_MB:
        #     logger.warning(f"Scraped data exceeds {MAX_FILE_SIZE_MB}MB. Truncating data.")
        #     # Optionally, you can truncate the jobs list
        #     while total_size_mb > MAX_FILE_SIZE_MB:
        #         jobs.pop()
        #         jobs_json_str = json.dumps(jobs, indent=4)
        #         total_size_mb = len(jobs_json_str.encode('utf-8')) / (1024 * 1024)
        
    except Exception as e:
        logger.error(f"Error occurred during job scraping: {e}")

@app.on_event("startup")
def startup_event():
    scheduler = BackgroundScheduler()
    scheduler.add_job(generate_jobs_json, "interval", hours=24)
    scheduler.start()
    logger.info("Scheduler started with interval job for generate_jobs_json.")

@app.get("/jobs")
def read_jobs(
    title: str = Query(None),
    location: str = Query(None),
    company: str = Query(None),
    site_name: str = Query(None),
    search_term: str = Query(None),
    distance: int = Query(50),
    is_remote: bool = Query(False),
    job_type: str = Query(None),
    easy_apply: bool = Query(None),
    results_wanted: int = Query(15),
    country_indeed: str = Query("usa"),
    description_format: str = Query("markdown"),
    linkedin_fetch_description: bool = Query(None),
    linkedin_company_ids: list[int] = Query(None),
    offset: int = Query(0),
    hours_old: int = Query(None),
    enforce_annual_salary: bool = Query(False),
    verbose: int = Query(2),
    proxies: list[str] = Query(None),
):
    try:
        jobs = json.loads(Path("jobs.json").read_text())
    except FileNotFoundError:
        return JSONResponse(content={"error": "jobs.json file not found"}, status_code=404)
    
    filtered_jobs = [job for job in jobs if
                     (title.lower() in job["title"].lower() if title else True) and
                     (location.lower() in job["location"].lower() if location else True) and
                     (company.lower() in job["company_name"].lower() if company else True)]
    return JSONResponse(content=filtered_jobs, status_code=200)

if __name__ == '__main__':
    logger.info("Starting FastAPI app...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
