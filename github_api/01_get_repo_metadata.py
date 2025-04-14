import requests
import json
from getpass import getpass
from datetime import datetime
import time
import random 
from ratelimit import limits

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

@limits(calls=30, period=ONE_MINUTE)
def get_response(stars):
    '''
    max number of request: 30 per minute
    '''
    # set url
    url_multiple_repos  = f'https://api.github.com/search/repositories?q=language:python+stars:{stars}'
    # send request
    response = requests.request('GET', url=url_multiple_repos, headers=headers, data=payload)
    if response.status_code != 200:
        print(f'Error with response. Check out status_code {response.status_code}!')

    else:
        # save response in variable 
        data = response.json()
        data = data['items'][0]
        # set timestamp as str
        timestamp = datetime.now(tz=None).strftime('%Y-%m-%d_%H-%H-%S')
        data['importtimestamp'] = timestamp

        return data
        # # save data from response as json in data/
        # with open(f'../data/raw_data/{page}_multiple_github_repos_page_{timestamp}.json', 'w') as file:
        #     json.dump(data, file)


def set_sleeper():
    # set sleeper
    random_number = random.randint(4,8)
    time.sleep(random_number)


# https://api.github.com/search/repositories?q=language:python
# repo: https://github.com/public-apis/public-apis/ has max_num of stars = 335520 (request date: 2025-04-13)
# for further work metadata of 1000 repos in total will be requested and saved
max_stars = 22196
step = 28
# empty list for page numbers with no response
stars_with_no_response = []
repo_data = []
num_of_request = 0
check = [100, 200, 300, 400, 500, 600, 700, 800, 900]

for stars in range(0, max_stars+1, step):
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
        print(f'Repo for {stars} was successfully append to repo_data.')
        if num_of_request in check:
            with open(f'../data/raw_data/checkpoint_{num_of_request}_multiple_github_repos.json', 'w') as file:
                json.dump(repo_data, file)
            
            print(f'Checkpoint {num_of_request} was saved.')

    
# save data from response as json in data/
with open(f'../data/raw_data/multiple_github_repos.json', 'w') as file:
    json.dump(repo_data, file)

print('Json file is created')

# if not stars_with_no_response:
#     print(f'Response of a repo with {stars} stars was saved into the directory data.') 
# else:
#     # temporary list to store pages with no response
#     tmp_list = []
#     # check pages with no response again
#     for page in stars_with_no_response:
#         set_sleeper()
#         if get_response(stars) is None:
#             tmp_list.append(stars)
#             continue
#         # add page with wrong response code to list
#         stars_with_no_response.append(stars)

# if tmp_list is not None:
#     pages_with_no_response = tmp_list
#     # save list for later analysis
#     with open(f'../data/helper/stars_with_wrong_response.json', 'w') as file:
#         json.dump(stars_with_no_response, file)
# else:
#     print('Getting repository metadata is finished.')


    