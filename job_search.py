import requests
import json
import math
import validators

"""
Script Name: job_search.py
Description: The purpose of this script is to run job searches on WorkDay based job listing sites.
Author: Ryan Triplett
Email: ryantrip@gmail.com
Version: 0.2

Todo:
* Add configuration file functionality, maybe via a parent orchestration script.
* Create more scripts that support other types of common job listing web applications.
* Add send email functionality for reporting.
* Automate script to run at an interval.
* Add logging.
"""

# The 'workday_url' is the base URL for the API. The 'search_text' is your search query.
# 'locations' is you location IDs. If you do not wish to set one or more parameters, set it to 'None'.
# For Nvidia
workday_url = 'https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs'
locations = ["c498fba66f4e01f896020488d5007305","91336993fab910af6d702fae0bb4c2e8","91336993fab910af6d716528e9d4c406"]
# For WorkDay
# workday_url = 'https://workday.wd5.myworkdayjobs.com/wday/cxs/workday/Workday/jobs'
# locations = ["5e834d290de7475ba43b61959f6a9d1c","289a125164674dd28c79bc9bb7e46fd8","9da5d518486801f61a50c4aedf1ab23f"]
search_text = 'Security'

# Set the limit for how many jobs are returned (max is 20), and configuring the data for the request with the search query and locations data.
# I do not recomend changing this value, as lowering it will increase the amount of requests made.
limit = 20

# Validate input
def validate_input(vworkday_url, vsearch_text, vlocations, vlimit):
    validation_pass = True
    if not validators.url(vworkday_url):
        print('Error: The "workday_url" variable is not set to a valid URL.')
        validation_pass = False
    if not isinstance(vsearch_text, str):
        print('Error: The "search_text" variable is not set to a valid string.')
        validation_pass = False
    if not isinstance(vlocations, list):
        print('Error: The "locations" variable is not set to a valid array.')
        validation_pass = False
    if vlimit > 20 or vlimit < 1 or vlimit % 1 != 0:
        print('Error: The "limit" variable can only be set to a whole number between 1 and 20.')
        validation_pass = False
    return validation_pass

# Function to create the payload for the request data.
def set_payload(psearch_text, plocations, plimit, poffset):
    payload_data = '{"appliedFacets":{'
    if plocations is not None:
        payload_data += '"locations":['
        for i, location in enumerate(plocations):
            if i != len(locations) - 1:
                payload_data += f'"{location}",'
            else:
                payload_data += f'"{location}"]}},'
    else:
        payload_data += '"locations":[]},'
    payload_data += f'"limit":{str(plimit)},"offset":{str(poffset)},"searchText":"{psearch_text}"}}'
    return payload_data

# Function to grab the job listings, and return them as a list.
def get_jobs(jworkday_url, jsearch_text, jlocations, jlimit):
    api_headers = {"Content-Type":"application/json"}
    job_list = []
    pages = 1
    page = 0
    while page < pages:
        if page == 0:
            payload = set_payload(jsearch_text, jlocations, jlimit, 0)
        else:
            payload = set_payload(jsearch_text, jlocations, jlimit, jlimit * page)
        api_response = requests.post(jworkday_url, headers = api_headers, data = payload)
        response_dict = json.loads(api_response.text)
        if page == 0:
            total_listings = response_dict['total']
            pages = math.ceil(total_listings / limit)
        for job_info in response_dict['jobPostings']:
                if 'title' in job_info:
                    job_list.append(job_info['title'])
        page += 1
    return job_list

# Function to filter listings by their title, looking for the 'search_text'.
def filter_listings(job_list, jsearch_text):
    relevant_listings = []
    for job in job_list:
        if jsearch_text != None and search_text != '':
            if jsearch_text.lower() in job.lower():
                relevant_listings.append(job)
        else:
            relevant_listings.append(job)
    return relevant_listings

# Run our functions to return the list of jobs, along with our filtered list of jobs.
def main():
    if validate_input(workday_url, search_text, locations, limit) == True:
        jobs = get_jobs(workday_url, search_text, locations, limit)
        relevant_jobs = filter_listings(jobs, search_text)

        # Print results.
        if len(jobs) != len(relevant_jobs):
            print(f'{len(jobs)} jobs found, {len(relevant_jobs)} of which contain the word "{search_text}" in the job title:')
        elif len(jobs) == 0:
            print('No jobs found.')
        else:
            print(f'{len(jobs)} jobs found:')

        for job in relevant_jobs:
            print(f'    {job}')
    else:
        print('Error: Ending program, input validation failed.')

# Exception handling.
try:
    main()
except:
    print('There was an error running the script.')
