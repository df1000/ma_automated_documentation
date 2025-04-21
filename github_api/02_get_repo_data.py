
import requests
import os
from dotenv import load_dotenv
from datetime import datetime # package for timestamps
import time # package to set time ranges
from ratelimit import limits, sleep_and_retry # package for handling api requests
import json
import pandas as pd
import random


load_dotenv(override=True)

# set ratelimit for requests
ONE_MINUTE = 60

# set credentials and parameters for api requests
ACCESS_TOKEN = os.environ['GIT_TOKEN']
PAYLOAD = {}
HEADERS = {
  'Accept': 'application/vnd.github+json',
  'X-GitHub-Api-Version': '2022-11-28',
  'Authorization': f'Bearer {ACCESS_TOKEN}'
}


def set_sleeper(number=None):
    '''
    Function which pauses execution of script for a specified or random amount of time.

    Args:
        number (optional): The number of seconds to pause. Defaults to None.

    Return:
        None
    '''
    if number != None: # check if number is not None
        time.sleep(number) # scrpipt pause for given number
    random_number = random.randint(3,8) # if not set time to random number
    time.sleep(random_number) # script pause for random number


@sleep_and_retry # set function in sleep until specified time periond of 1 minute is over
@limits(calls=10, period=ONE_MINUTE) # limits number of requests to 10 per minute
def check_repo_for_readme(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/readme"

    response = requests.get(url, headers=HEADERS, data=PAYLOAD)
    if response.status_code == 404:
        print(f'Repo {repo_name} has no README.md.')
        return False
    elif response.status_code == 200:
        return True
    else:
        if response.status_code != 200: # check if status_code is not 200 to prevent time outs and banning from api
            print(f'Error with response. Check out status_code {response.status_code}!')
            rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining')) # get remaining rate limit for requests
            if rate_limit_remaining <= 1: # if rate limits are <= 1 call set_sleeper func and return None
                set_sleeper(61)
        return False


def check_num_of_files(repo_owner, repo_name, refs):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/git/trees/{refs}?recursive=1'
    response = requests.request("GET", url, headers=HEADERS, data=PAYLOAD) 
    if response.status_code != 200: # check if status_code is not 200 to prevent time outs and banning from api
        print(f'Error with response. Check out status_code {response.status_code}!')
        rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining')) # get remaining rate limit for requests
        if rate_limit_remaining <= 1: # if rate limits are <= 1 call set_sleeper func and return None
            set_sleeper(61)
            return False
            
    data = response.json()
    blob_count = sum(1 for item in data["tree"] if item["type"] == "blob") # count files of type 'blob'
    if blob_count < 1000:
        return True
    else:
        return False
    

@sleep_and_retry # set function in sleep until specified time periond of 1 minute is over
@limits(calls=10, period=ONE_MINUTE) # limits number of requests to 10 per minute
def download_github_repo(repo_owner, repo_name, refs):

    # https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#download-a-repository-archive-zip
    # api has a limit of 1000 files and 100 MB/file per repo (https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28)
    
    url =   f'https://api.github.com/repos/{repo_owner}/{repo_name}/zipball/{refs}'
    
    # Send a request to the URL
    response = requests.get(url, stream=True, headers=HEADERS, data=PAYLOAD)
    
    # Check if the request was successful
    if response.status_code == 200:
        timestamp = datetime.now(tz=None).strftime('%Y-%m-%d_%H-%M-%S')
        with open(f"../data/repo_data/{repo_owner}_{repo_name}_{timestamp}.zip", "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"Repository '{repo_name}' has been downloaded as a ZIP file.")
    else:
        if response.status_code != 200: # check if status_code is not 200 to prevent time outs and banning from api
            print(f'Error with response. Check out status_code {response.status_code}!')
            rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining')) # get remaining rate limit for requests
            if rate_limit_remaining <= 1: # if rate limits are <= 1 call set_sleeper func and return None
                set_sleeper(61)



# open json as dataframe
file_path = '../data/df_repos_sample_250.json'
with open(file_path, 'r') as file:
    loaded_data = json.load(file)

df = pd.DataFrame(data=loaded_data)
repos = df['full_name'].tolist()

num_of_repos = 0
for repo in repos:
    repo_owner = repo.split('/')[0]
    repo_name = repo.split('/')[1]
    refs = df.loc[df['full_name'] == repo, 'default_branch'].iloc[0]

    check_readme = check_repo_for_readme(repo_owner, repo_name) 
    check_files = check_num_of_files(repo_owner, repo_name, refs)  

    if check_readme and check_files:
        download_github_repo(repo_owner, repo_name, refs) 
        num_of_repos += 1
    else:
        print(f'{repo} has no README.md or size is to big.')
        continue

    if num_of_repos == 200:
        break
