import requests # package for api requests
import json # package to work with .json
from getpass import getpass # package for handing over credentials
from datetime import datetime # package for timestamps
import time # package to set time ranges
import random # package to work with random numbers
from ratelimit import limits, sleep_and_retry # package for handling api requests


# set ratelimit for requests
ONE_MINUTE = 60

# set credentials and parameters for api requests
ACCESS_TOKEN = getpass()
payload = {}
headers = {
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
@limits(calls=20, period=ONE_MINUTE) # limits number of requests to 20 per minute
def get_response(stars, num_of_requests):
    '''
    Function which sends request to search endpoint for repositories with a given number of stars for GitHub api and saves 
    the response as .json.

    Args:
        stars: The number of stars of a repository.
        num_of_requests: The number of request for tracking the process.

    Return:
        data
    '''
    # set url for search endpoint with a range of to increase the propability of a postive response
    url_multiple_repos  = f'https://api.github.com/search/repositories?q=language:python+stars:{stars}..{stars+15}'
    response = requests.request('GET', url=url_multiple_repos, headers=headers, data=payload)# send GET request (1/2)
    if response.status_code != 200: # check if status_code is not 200 to prevent time outs and banning from api
        print(f'Error with response. Check out status_code {response.status_code}!')
        rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining')) # get remaining rate limit for requests
        if rate_limit_remaining <= 1: # if rate limits are <= 1 call set_sleeper func and return None
            set_sleeper(61)
        return None 

    else:
        data = response.json() # save response in variable 
        try:
            data = data['items'][-1] # get last element of .json
            # why last element? request has a range and results are sorted desc
            # i want the element with the lowest number of stars because it is closer to the defined step size
        except IndexError: # expection for index error --> send second response with wider range
            print(f'For request {num_of_request} index is out of range. Response got no data.')
            set_sleeper(3) # call set_sleeper func to prevent pushing rate limits
            url_multiple_repos  = f'https://api.github.com/search/repositories?q=language:python+stars:{stars}..{stars+25}' 
            response = requests.request('GET', url=url_multiple_repos, headers=headers, data=payload) # send GET request (2/2)
            if response.status_code != 200: # check if status_code is not 200 to prevent time outs and banning from api
                print(f'Error with response. Check out status_code {response.status_code}!')
                return None

            data = response.json() # save response in variable 

            try:
                data = data['items'][-1] # get last element of .json
                print('Request with range find data.')
            except IndexError: # if another index error is raised return None and go to next iteration in for loop
                print(f'For second try, the request {num_of_request} index is out of range. Response got no data.')
                return None
            
        timestamp = datetime.now(tz=None).strftime('%Y-%m-%d_%H-%M-%S') # set timestamp as str for further analysis
        data['importtimestamp'] = timestamp # add timestamp as key-value pair to data

        return data


# parameter to get metadata based on response of first request --> only specification: code has to be written in Python
# https://api.github.com/search/repositories?q=language:python --> repo with maximum number of stars: https://github.com/public-apis/public-apis/ --> stars = 335520 (request date: 2025-04-13)

# for further work metadata of 1000 repos in total will be requested and saved
max_stars = 22196 # 75% quantil of first response from GitHub api --> for further analysis all repos from 22196 up to 335520 stars will used
start = 0 # minimum of stars
step = 28 # step size for iteration
stars_with_no_response = [] # empty list for page numbers with no response
repo_data = [] # empty list to save repo data
num_of_request = 0

# list with checkpoints
check = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 795]

# iterate over range of stars 0-22196 in step size 28
for stars in range(start, max_stars+1, step):
    if stars >= 22196: # check if stars >= 22196
        # save metadata of last iterations in json and break loop to stop script
        with open(f'../data/raw_data/checkpoint_{num_of_request}_multiple_github_repos_last.json', 'w') as file:
            json.dump(repo_data, file)
        break
    set_sleeper() # call sleeper func    
    num_of_request += 1 # increase number of request +1
    data = get_response(stars, num_of_request) # call get_response func and save result in variable
    
    if data == None: # check if data contains values
        stars_with_no_response.append(stars) # add page with wrong response code to list

    else:
        repo_data.append(data) # if data contains values, append data to list repo_data
        print(f'Request nr. {num_of_request}: for repo with {stars} (+ up to 15-25) stars was successfully append to repo_data.')
        
    if num_of_request in check: # check if num_of_request is in list check and if yes, save content of repo_data in .json
        with open(f'../data/raw_data/checkpoint_{num_of_request}_multiple_github_repos.json', 'w') as file:
            json.dump(repo_data, file)
        
        print(f'Checkpoint {num_of_request} was saved.')
        repo_data = [] # create new empty instance for repo_data to save the response of further requests

# save list for later analysis
with open(f'../data/helper/stars_with_wrong_response.json', 'w') as file:
    json.dump(stars_with_no_response, file)    



    