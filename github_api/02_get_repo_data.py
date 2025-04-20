
import requests
import os
from dotenv import load_dotenv
from datetime import datetime # package for timestamps
import time # package to set time ranges
from ratelimit import limits, sleep_and_retry # package for handling api requests
import json
import pandas as pd


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


@sleep_and_retry # set function in sleep until specified time periond of 1 minute is over
@limits(calls=30, period=ONE_MINUTE) # limits number of requests to 20 per minute
def check_repo_for_readme(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/readme"
    
    response = requests.get(url, headers=HEADERS, data=PAYLOAD)
    if response.status_code == 404:
        print(f'Repo {repo_name} has no README.md.')
        return False
    elif response.status_code == 200:
        return True
    else:
        print(f'Error with url: {response.status_code}')
        return False



@sleep_and_retry # set function in sleep until specified time periond of 1 minute is over
@limits(calls=30, period=ONE_MINUTE) # limits number of requests to 20 per minute
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
        print(f"Failed to download repository. HTTP Status Code: {response.status_code}")


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

    if check_repo_for_readme(repo_owner, repo_name):
        download_github_repo(repo_owner, repo_name, refs) 
        num_of_repos += 1
    else:
        continue

    if num_of_repos == 200:
        break
