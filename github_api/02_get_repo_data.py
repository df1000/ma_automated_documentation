import requests
import os
from dotenv import load_dotenv
from datetime import datetime # package for timestamps
import time # package to set time ranges
from ratelimit import limits, sleep_and_retry # package for handling api requests


load_dotenv(override=True)

# set ratelimit for requests
ONE_MINUTE = 60

# set credentials and parameters for api requests
ACCESS_TOKEN = os.environ['GIT_TOKEN']
payload = {}
headers = {
  'Accept': 'application/vnd.github+json',
  'X-GitHub-Api-Version': '2022-11-28',
  'Authorization': f'Bearer {ACCESS_TOKEN}'
}


@sleep_and_retry # set function in sleep until specified time periond of 1 minute is over
@limits(calls=20, period=ONE_MINUTE) # limits number of requests to 20 per minute
def check_repo_for_readme(repo_owner, repo_name):
    url = f"https://github.com/{repo_owner}/{repo_name}/archive/refs/heads/main.zip"
    
    # Send a request to the URL
    response = requests.get(url, stream=True, headers=headers, data=payload)



@sleep_and_retry # set function in sleep until specified time periond of 1 minute is over
@limits(calls=20, period=ONE_MINUTE) # limits number of requests to 20 per minute
def download_github_repo(repo_owner, repo_name):
    # check if repo contains a readme
    # https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#download-a-repository-archive-zip
    url = f"https://github.com/{repo_owner}/{repo_name}/readme"
    
    # Send a request to the URL
    response = requests.get(url, stream=True, headers=headers, data=payload)
    
    # Check if the request was successful
    if response.status_code == 200:
        timestamp = datetime.now(tz=None).strftime('%Y-%m-%d_%H-%M-%S')
        with open(f"../data/repo_data/{repo_owner}_{repo_name}_{timestamp}.zip", "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Repository '{repo_name}' has been downloaded as a ZIP file.")
    else:
        print(f"Failed to download repository. HTTP Status Code: {response.status_code}")


repo_owner = 'taniiishk'
repo_name = 'rock-paper-scissors-game'

download_github_repo(repo_owner, repo_name) 
