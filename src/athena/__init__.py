from __future__ import annotations

import pandas as pd
import json
from pathlib import Path
from typing import Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from .jobs import JobType, Location
from .scrapers.utils import logger, set_logger_level, extract_salary
from .scrapers.indeed import IndeedScraper
from .scrapers.ziprecruiter import ZipRecruiterScraper
from .scrapers.glassdoor import GlassdoorScraper
from .scrapers.linkedin import LinkedInScraper
from .scrapers import SalarySource, ScraperInput, Site, JobResponse, Country
from .scrapers.exceptions import (
    LinkedInException,
    IndeedException,
    ZipRecruiterException,
    GlassdoorException,
)


def export_jobs_to_json(jobs, filename='jobs.json'):
    with open(filename, 'w') as f:
        json.dump(jobs, f, indent=4)

def transform_job_data(job):
    compensation = job.compensation.dict() if job.compensation else None
    return {
        "id": job.id,
        "title": job.title,
        "company_name": job.company_name,
        "location": job.location.display_location() if job.location else "",
        "job_url": job.job_url,
        "description": job.description,
        "date_posted": job.date_posted.isoformat() if job.date_posted else "",
        "job_type": [jt.value[0] for jt in job.job_type] if job.job_type else [],
        "is_remote": job.is_remote,
        "compensation": {
            "interval": compensation["interval"].value if compensation and compensation["interval"] else "",
            "min_amount": compensation["min_amount"] if compensation else None,
            "max_amount": compensation["max_amount"] if compensation else None,
            "currency": compensation["currency"] if compensation else ""
        } if compensation else None
    }

def scrape_jobs(
    site_name: str | list[str] | Site | list[Site] | None = None,
    search_term: str | None = None,
    location: str | None = None,
    distance: int | None = 50,
    is_remote: bool = False,
    job_type: str | None = None,
    easy_apply: bool | None = None,
    results_wanted: int = 15,
    country_indeed: str = "usa",
    hyperlinks: bool = False,
    proxies: list[str] | str | None = None,
    description_format: str = "markdown",
    linkedin_fetch_description: bool | None = False,
    linkedin_company_ids: list[int] | None = None,
    offset: int | None = 0,
    hours_old: int = None,
    enforce_annual_salary: bool = False,
    verbose: int = 2,
    **kwargs,
) -> pd.DataFrame:
    """
    Simultaneously scrapes job data from multiple job sites.
    :return: pandas dataframe containing job data
    """
    SCRAPER_MAPPING = {
        Site.LINKEDIN: LinkedInScraper,
        Site.INDEED: IndeedScraper,
        Site.ZIP_RECRUITER: ZipRecruiterScraper,
        Site.GLASSDOOR: GlassdoorScraper,
    }
    set_logger_level(verbose)

    def map_str_to_site(site_name: str) -> Site:
        return Site[site_name.upper()]

    def get_enum_from_value(value_str):
        for job_type in JobType:
            if value_str in job_type.value:
                return job_type
        raise Exception(f"Invalid job type: {value_str}")

    job_type = get_enum_from_value(job_type) if job_type else None

    def get_site_type():
        site_types = list(Site)
        if isinstance(site_name, str):
            site_types = [map_str_to_site(site_name)]
        elif isinstance(site_name, Site):
            site_types = [site_name]
        elif isinstance(site_name, list):
            site_types = [
                map_str_to_site(site) if isinstance(site, str) else site
                for site in site_name
            ]
        return site_types

    country_enum = Country.from_string(country_indeed)

    scraper_input = ScraperInput(
        site_type=get_site_type(),
        country=country_enum,
        search_term=search_term,
        location=location,
        distance=distance,
        is_remote=is_remote,
        job_type=job_type,
        easy_apply=easy_apply,
        description_format=description_format,
        linkedin_fetch_description=linkedin_fetch_description,
        results_wanted=results_wanted,
        linkedin_company_ids=linkedin_company_ids,
        offset=offset,
        hours_old=hours_old,
    )

    def scrape_site(site: Site) -> Tuple[str, JobResponse]:
        scraper_class = SCRAPER_MAPPING[site]
        scraper = scraper_class(proxies=proxies)
        scraped_data: JobResponse = scraper.scrape(scraper_input)
        cap_name = site.value.capitalize()
        site_name = "ZipRecruiter" if cap_name == "Zip_recruiter" else cap_name
        logger.info(f"{site_name} finished scraping")
        return site.value, scraped_data

    site_to_jobs_dict = {}

    def worker(site):
        site_val, scraped_info = scrape_site(site)
        return site_val, scraped_info

    with ThreadPoolExecutor() as executor:
        future_to_site = {
            executor.submit(worker, site): site for site in scraper_input.site_type
        }

        for future in as_completed(future_to_site):
            site_value, scraped_data = future.result()
            site_to_jobs_dict[site_value] = scraped_data

    def convert_to_annual(job_data: dict):
        if job_data["interval"] == "hourly":
            job_data["min_amount"] *= 2080
            job_data["max_amount"] *= 2080
        if job_data["interval"] == "monthly":
            job_data["min_amount"] *= 12
            job_data["max_amount"] *= 12
        if job_data["interval"] == "weekly":
            job_data["min_amount"] *= 52
            job_data["max_amount"] *= 52
        if job_data["interval"] == "daily":
            job_data["min_amount"] *= 260
            job_data["max_amount"] *= 260
        job_data["interval"] = "yearly"

    jobs_dfs: list[pd.DataFrame] = []
    job_list = []

    for site, job_response in site_to_jobs_dict.items():
        for job in job_response.jobs:
            job_data = transform_job_data(job)
            job_list.append(job_data)

    export_jobs_to_json(job_list)

    return pd.DataFrame(job_list)
