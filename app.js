//saved for testing purposes

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';
import dotenv from 'dotenv';

dotenv.config();

function App() {
  const [jobs, setJobs] = useState([]);
  const [title, setTitle] = useState('');
  const [location, setLocation] = useState('');
  const [company, setCompany] = useState('');
  const [siteName, setSiteName] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [distance, setDistance] = useState(50);
  const [isRemote, setIsRemote] = useState(false);
  const [jobType, setJobType] = useState('');
  const [easyApply, setEasyApply] = useState(false);
  const [resultsWanted, setResultsWanted] = useState(10);
  const [countryIndeed, setCountryIndeed] = useState('usa');
  const [descriptionFormat, setDescriptionFormat] = useState('markdown');
  const [linkedinFetchDescription, setLinkedinFetchDescription] = useState(false);
  const [linkedinCompanyIds, setLinkedinCompanyIds] = useState('');
  const [offset, setOffset] = useState(0);
  const [hoursOld, setHoursOld] = useState(null);
  const [enforceAnnualSalary, setEnforceAnnualSalary] = useState(false);
  const [verbose, setVerbose] = useState(2);
  const [proxies, setProxies] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = () => {
    axios.get('http://localhost:8000/jobs', {
      params: {
        title,
        location,
        company,
        site_name: siteName,
        search_term: searchTerm,
        distance,
        is_remote: isRemote,
        job_type: jobType,
        easy_apply: easyApply,
        results_wanted: resultsWanted,
        country_indeed: countryIndeed,
        description_format: descriptionFormat,
        linkedin_fetch_description: linkedinFetchDescription,
        linkedin_company_ids: linkedinCompanyIds ? linkedinCompanyIds.split(',').map(id => parseInt(id, 10)) : [],
        offset,
        hours_old: hoursOld,
        enforce_annual_salary: enforceAnnualSalary,
        verbose,
        proxies: proxies ? proxies.split(',') : []
      }
    })
      .then(response => {
        setJobs(response.data);
      })
      .catch(error => {
        console.error('There was an error fetching the data!', error);
      });
  };

  const handleFilterChange = () => {
    fetchJobs();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Job Listings</h1>
        <div className="filter-container">
          <input type="text" placeholder="Job Title" value={title} onChange={e => setTitle(e.target.value)} />
          <input type="text" placeholder="Location" value={location} onChange={e => setLocation(e.target.value)} />
          <input type="text" placeholder="Company" value={company} onChange={e => setCompany(e.target.value)} />
          <input type="text" placeholder="Site Name" value={siteName} onChange={e => setSiteName(e.target.value)} />
          <input type="text" placeholder="Search Term" value={searchTerm} onChange={e => setSearchTerm(e.target.value)} />
          <input type="number" placeholder="Distance" value={distance} onChange={e => setDistance(parseInt(e.target.value, 10))} />
          <input type="checkbox" checked={isRemote} onChange={e => setIsRemote(e.target.checked)} /> Remote
          <input type="text" placeholder="Job Type" value={jobType} onChange={e => setJobType(e.target.value)} />
          <input type="checkbox" checked={easyApply} onChange={e => setEasyApply(e.target.checked)} /> Easy Apply
          <input type="number" placeholder="Results Wanted" value={resultsWanted} onChange={e => setResultsWanted(parseInt(e.target.value, 10))} />
          <input type="text" placeholder="Country Indeed" value={countryIndeed} onChange={e => setCountryIndeed(e.target.value)} />
          <select value={descriptionFormat} onChange={e => setDescriptionFormat(e.target.value)}>
            <option value="markdown">Markdown</option>
            <option value="html">HTML</option>
          </select>
          <input type="checkbox" checked={linkedinFetchDescription} onChange={e => setLinkedinFetchDescription(e.target.checked)} /> LinkedIn Fetch Description
          <input type="text" placeholder="LinkedIn Company IDs (comma-separated)" value={linkedinCompanyIds} onChange={e => setLinkedinCompanyIds(e.target.value)} />
          <input type="number" placeholder="Offset" value={offset} onChange={e => setOffset(parseInt(e.target.value, 10))} />
          <input type="number" placeholder="Hours Old" value={hoursOld || ''} onChange={e => setHoursOld(e.target.value ? parseInt(e.target.value, 10) : null)} />
          <input type="checkbox" checked={enforceAnnualSalary} onChange={e => setEnforceAnnualSalary(e.target.checked)} /> Enforce Annual Salary
          <input type="number" placeholder="Verbose" value={verbose} onChange={e => setVerbose(parseInt(e.target.value, 10))} />
          <input type="text" placeholder="Proxies (comma-separated)" value={proxies} onChange={e => setProxies(e.target.value)} />
          <button onClick={handleFilterChange}>Filter</button>
        </div>
        {jobs.length > 0 ? (
          <ul>
            {jobs.map((job, index) => (
              <li key={index}>
                <h2>{job.title}</h2>
                <p><strong>Company:</strong> {job.company_name}</p>
                <p><strong>Location:</strong> {job.location}</p>
                <p><strong>Date Posted:</strong> {job.date_posted}</p>
                <a href={job.job_url} target="_blank" rel="noopener noreferrer">Job Link</a>
              </li>
            ))}
          </ul>
        ) : (
          <p>Loading...</p>
        )}
      </header>
    </div>
  );
}

export default App;
