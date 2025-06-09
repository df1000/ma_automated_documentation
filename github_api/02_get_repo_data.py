# Author: Lisa Wallner
# Description: In this Python script data of multiple GitHub repositories via the API based on previous collected repository metadata will be requested. 
# Depedencies:
#   - github_api/01_get_repo_metadata.py
#   - preprocessing/01_repos_metadata.ipynb
#   - preprocessing/02_analyse_repos_metadata.ipynb
#   - preprocessing/03_get_split_of_repos.ipynb
#   - data/helper/repos_downloaded_zip.json
#
# Hint: If lines are created with support of a Large Language Model or the code is taken from another source, you find following hint at the end of the line:
#       (generated with Microsoft Copilot) or (source: link_to_source)


import requests # package for api requests
import os # package for using operating system
from dotenv import load_dotenv
from datetime import datetime # package for timestamps
import time # package to set time ranges
from ratelimit import limits, sleep_and_retry # package for handling api requests
import json # package to work with .json
import pandas as pd # package for data manipulation
import random # package to work with random numbers

# load .env file
load_dotenv(override=True)

# set ratelimit for requests
ONE_MINUTE = 60

# set credentials and parameters for api requests
ACCESS_TOKEN = os.environ['GIT_TOKEN'] # get token from .env
PAYLOAD = {}
HEADERS = {
  'Accept': 'application/vnd.github+json',
  'X-GitHub-Api-Version': '2022-11-28',
  'Authorization': f'Bearer {ACCESS_TOKEN}'
}


def check_repo_processed(repo_owner, repo_name):
    '''
    Function which checks if a GitHub repository is already downloaed as ZIP file.

    Args:
        repo_owner: The name of the GitHub repository owner.
        repo_name: The name of the GitHub repository.

    Return:
        Boolean
    '''
    try: # try to open the documentation file
        repo_to_check = [repo_owner, repo_name] # list with two values --> repo to check
        with open('../data/helper/repos_downloaded_zip.json', 'r') as file: # open and load documentation file which contains information about previous loaded repositories
            data_list = json.load(file) # save loaded content in variable data_list
    except json.JSONDecodeError: # raise exception if JSONDecodeError --> documentation file is empty
        data_list = [] # create new empty list
        print(f'Repo "{repo_name}" from "{repo_owner} is not downloaded.')

    if repo_to_check in data_list: # check if repository is already downloaded
        print(f'Repo "{repo_name}" from "{repo_owner} is already downloaded.')
        return True
    else: 
        return False
    

def write_preprocessed_repo(repo_owner, repo_name):
    '''
    Function which writes the owner and the name of the GitHub repository to a documentation file, if the repository is
    alread processed.
    Path of the documentation file: '../data/helper/repos_downloaded_zip.json'

    Args:
        repo_owner: The name of the GitHub repository owner.
        repo_name: The name of the GitHub repository.

    Return:
        None
    '''
    path = '../data/helper/repos_downloaded_zip.json' # path where the documentation file is saved
    try: # try to open the documentation file
        with open(path, 'r') as file: # open and load documentation file which contains information about previous loaded repositories
            data_list = json.load(file) # save loaded content in variable data_list
    except json.JSONDecodeError: # raise exception if JSONDecodeError --> documentation file is empty
        data_list = [] # create new empty list

    new_entry = [repo_owner, repo_name] # create new sublist with processed repository
    data_list.append(new_entry) # append sublist 'new_entry' to existing data_list

    with open(path, 'w') as file: # open documentation file and save data_list
        json.dump(data_list, file)


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
    '''
    Function which checks repository if it contains a README.md.

    Args: 
        repo_owner: Owner of the GitHub repository.
        repo_name: Name of the GitHub repository.
    
    Return: 
        Boolean  
    '''
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/readme' # url to check if repo has README.md
    response = requests.get(url, headers=HEADERS, data=PAYLOAD) # send GET request
    if response.status_code == 404: # check if status_code is 404 --> repo has no README.md
        print(f'Repo {repo_name} has no README.md.')
        return False
    elif response.status_code == 200: # check if status_code is 200 --> repo has README.md
        print(f'Repo {repo_name} has README.md.')
        return True
    else:
        if response.status_code != 200: # check if status_code is not 200 to prevent time outs and banning from api
            print(f'Error with response. Check out status_code {response.status_code}!')
            rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining')) # get remaining rate limit for requests
            if rate_limit_remaining <= 1: # if rate limits are <= 1 call set_sleeper func and return None
                set_sleeper(61)
        return False


def check_num_of_files(repo_owner, repo_name, refs):
    '''
    Function which checks the number of files within the GitHub repository.

    Args:
        repo_owner: Owner of the GitHub repository.
        repo_name: Name of the GitHub repository.
        refs: Name of branch.
    
    Return:
        Boolean
    '''
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/git/trees/{refs}?recursive=1' # url to check get all files
    response = requests.request("GET", url, headers=HEADERS, data=PAYLOAD) # send GET request
    if response.status_code != 200: # check if status_code is not 200 to prevent time outs and banning from api
        print(f'Error with response. Check out status_code {response.status_code}!')
        rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining')) # get remaining rate limit for requests
        if rate_limit_remaining <= 1: # if rate limits are <= 1 call set_sleeper func and return None
            set_sleeper(61)
   
            return False
            
    data = response.json() # save response in variable 
    try:
        # count files of type 'blob'
        # iterate over all files in the key-value-pairs and set 1 if type == 'blob' (blob indicates a file)
        # sum all 1's --> number of files in one repository
        # https://docs.github.com/en/rest/git/trees?apiVersion=2022-11-28
        blob_count = sum(1 for item in data["tree"] if item["type"] == "blob")  # (generated with Microsoft Copilot)
    except KeyError as e: # raise exception if a KeyError occurs to prevent the code for failing
        print('Key error in data["tree"]. Maybe repo was further developed.') 
        # there can be a time offset between the timestamp where the metadata of the repository and the repository in general were collected
        # it cannot be ruled out that there will be further development in repository
        return False
    if blob_count < 1000: 
        return True
    else:
        print('Repo is to big.')
        return False
    

@sleep_and_retry # set function in sleep until specified time periond of 1 minute is over
@limits(calls=10, period=ONE_MINUTE) # limits number of requests to 10 per minute
def download_github_repo(repo_owner, repo_name, refs):
    '''
    Function which downloads the GitHub repository as ZIP file if the number of files is smaller than 1000.
    https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#download-a-repository-archive-zip
    The GitHub api has limit of 1000 files and 100 MB/file for a repository.
    https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28

    Args:
        repo_owner: Owner of the GitHub repository.
        repo_name: Name of the GitHub repository.
        refs: Name of branch.

    Return:
        None
    '''  
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/zipball/{refs}' # url to download repo a zip file for specific branch (refs)
    response = requests.get(url, stream=True, headers=HEADERS, data=PAYLOAD) # send GET request (generated with Microsoft Copilot)
    if response.status_code == 200: # check if request was successful --> status_code == 200
        timestamp = datetime.now(tz=None).strftime('%Y-%m-%d_%H-%M-%S') # set timestamp
        with open(f"../data/repo_data_zip/{repo_owner}_{repo_name}_{timestamp}.zip", "wb") as file: # create zip file for repo
            for chunk in response.iter_content(chunk_size=8192): # iterate over each chunk (chunk_size=8192) in response data to prevent memory constraints
                file.write(chunk) # write chunk to zip file
        print(f"Repository '{repo_name}' has been downloaded as a ZIP file.")
    else:
        if response.status_code != 200: # check if status_code is not 200 to prevent time outs and banning from api
            print(f'Error with response. Check out status_code {response.status_code}!')
            rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining')) # get remaining rate limit for requests
            if rate_limit_remaining <= 1: # if rate limits are <= 1 call set_sleeper func and return None
                set_sleeper(61)


file_path = '../data/df_repos_sample_250.json' 
with open(file_path, 'r') as file:
    loaded_data = json.load(file) # save .json content with repository metadata as variable

df = pd.DataFrame(data=loaded_data) # create dataframe
repos = df['full_name'].tolist() # create a list with all repository identification (repo_owner/repo_name)

num_of_repos = 0 # set counter
#cnt = 0 # for testing

for repo in repos: # iterate overall repositorys in repos list
    # if cnt >=2: # for testing
    #     break
    repo_owner = repo.split('/')[0] # create variable repo_owner
    repo_name = repo.split('/')[1] # create variable repo_name
    refs = df.loc[df['full_name'] == repo, 'default_branch'].iloc[0] # get default branch from metadata and save it in variable

    if not check_repo_processed(repo_owner, repo_name):
        check_readme = check_repo_for_readme(repo_owner, repo_name) # call check_repo_for_readme func
        check_files = check_num_of_files(repo_owner, repo_name, refs) # call check_num_of_files func
        if check_readme and check_files: # if check_readme and check_files are TRUE 
            print('---------------------------------------------')
            print(f'Repo {repo_name} from {repo_owner} will be downloaded.')
            download_github_repo(repo_owner, repo_name, refs) # call download_github_repo func to get repository content as zip file
            write_preprocessed_repo(repo_owner=repo_owner, repo_name=repo_name)
            num_of_repos += 1 # increase counter num_of_repos
            #cnt += 1 # for testing
        else: # if check_readme and / or check_files is FALSE then process the next repository
            print(f'{repo} will not be downloaded. Continue with the next one.')
            print('---------------------------------------------')
            continue

    if num_of_repos == 200: # if counter num_of_repos == 200 --> break
        break
