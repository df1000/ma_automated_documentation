import requests
import json
from getpass import getpass
from datetime import datetime
import time
import random 
from ratelimit import limits, sleep_and_retry

# set ratelimit
ONE_MINUTE = 60

# set credentials
ACCESS_TOKEN = getpass()
payload = {}
headers = {
  'Accept': 'application/vnd.github+json',
  'X-GitHub-Api-Version': '2022-11-28',
  'Authorization': f'Bearer {ACCESS_TOKEN}'
}


def set_sleeper(number=None):
    # set sleeper
    if number != None:
        time.sleep(number)
    random_number = random.randint(3,8)
    time.sleep(random_number)


@sleep_and_retry
@limits(calls=20, period=ONE_MINUTE)
def get_response(stars):
    '''
    max number of request: 30 per minute
    '''
    # set url
    url_multiple_repos  = f'https://api.github.com/search/repositories?q=language:python+stars:{stars}..{stars+15}'
    # send request
    response = requests.request('GET', url=url_multiple_repos, headers=headers, data=payload)
    if response.status_code != 200:
        print(f'Error with response. Check out status_code {response.status_code}!')
        rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining'))
        if rate_limit_remaining <= 1:
            set_sleeper(61)
        return None

    else:
        # save response in variable 
        data = response.json()

        try:
            data = data['items'][-1]
        except IndexError:
            print('Index is out of range. Response got no data.')
            # send second response with range
            set_sleeper(3)
            url_multiple_repos  = f'https://api.github.com/search/repositories?q=language:python+stars:{stars}..{stars+25}'
            response = requests.request('GET', url=url_multiple_repos, headers=headers, data=payload)
            if response.status_code != 200:
                print(f'Error with response. Check out status_code {response.status_code}!')
                return None

            data = response.json()

            try:
                data = data['items'][-1]
                print('Request with range find data.')
            except IndexError:
                print('Index is out of range. Response got no data.')
                return None
            
        # set timestamp as str
        timestamp = datetime.now(tz=None).strftime('%Y-%m-%d_%H-%M-%S')
        data['importtimestamp'] = timestamp

        return data



# https://api.github.com/search/repositories?q=language:python
# repo: https://github.com/public-apis/public-apis/ has max_num of stars = 335520 (request date: 2025-04-13)
# for further work metadata of 1000 repos in total will be requested and saved
max_stars = 22196
start = 15372 #0
step = 28
# empty list for page numbers with no response
stars_with_no_response = []
repo_data = []
num_of_request = 551 #0
check = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 768]

for stars in range(start, max_stars+1, step):
    if stars > 22196:
        break
    set_sleeper()    
    data = get_response(stars)
    num_of_request += 1
    
    if data == None:
        # add page with wrong response code to list
        stars_with_no_response.append(stars)
        continue
    else:
        repo_data.append(data)
        print(f'Request nr. {num_of_request}: for repo with {stars} (+ up to 15-25) stars was successfully append to repo_data.')
        if num_of_request in check:
            with open(f'../data/raw_data/checkpoint_{num_of_request}_multiple_github_repos.json', 'w') as file:
                json.dump(repo_data, file)
            
            print(f'Checkpoint {num_of_request} was saved.')
            repo_data = []

    

with open(f'../data/helper/stars_with_wrong_response.json', 'w') as file:
    json.dump(stars_with_no_response, file)



    