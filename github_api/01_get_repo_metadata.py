import requests
import json
from getpass import getpass
from datetime import datetime
import time
import random 

# set credentials
ACCESS_TOKEN = getpass()
payload = {}
headers = {
  'Accept': 'application/vnd.github+json',
  'X-GitHub-Api-Version': '2022-11-28',
  'Authorization': f'Bearer {ACCESS_TOKEN}'
}

def get_response(stars):
    # set url
    url_multiple_repos  = f'https://api.github.com/search/repositories?q=language:python+stars:={stars}'
    # send request
    response = requests.request('GET', url=url_multiple_repos, headers=headers, data=payload)
    if response.status_code != 200:
        print(f'Error with response. Check out status_code {response.status_code}!')

        return stars
    else:
        # save response in variable 
        data = response.json()
        # set timestamp as str
        timestamp = datetime.now(tz=None).strftime('%Y-%m-%d_%H-%H-%S')
        # save data from response as json in data/
        with open(f'../data/raw_data/{page}_multiple_github_repos_page_{timestamp}.json', 'w') as file:
            json.dump(data, file)


def set_sleeper():
    # set sleeper
    random_number = random.randint(4,8)
    time.sleep(random_number)


# https://api.github.com/search/repositories?q=language:python
# repo: https://github.com/public-apis/public-apis/ has max_num of stars = 335520 (request date: 2025-04-13)
# for further work metadata of 1000 repos in total will be requested and saved
# to give an overview of the functionality of the code / performance of the llm repos with min_stars = 0 to max_stars = 335520 (--> step: 335 stars)
# will be collected
max_stars = 335520
step = 335
# empty list for page numbers with no response
stars_with_no_response = []


for stars in range(0, max_stars+1, step):
    set_sleeper()    
    if get_response(stars) == None:
        continue
    # add page with wrong response code to list
    stars_with_no_response.append(stars)

if not stars_with_no_response:
    print(f'Response of a repo with {stars} stars was saved into the directory data.') 
else:
    # temporary list to store pages with no response
    tmp_list = []
    # check pages with no response again
    for page in stars_with_no_response:
        set_sleeper()
        if get_response(stars) is None:
            tmp_list.append(stars)
            continue
        # add page with wrong response code to list
        stars_with_no_response.append(stars)

if tmp_list is not None:
    pages_with_no_response = tmp_list
    # save list for later analysis
    with open(f'../data/helper/stars_with_wrong_response.json', 'w') as file:
        json.dump(stars_with_no_response, file)
else:
    print('Getting repository metadata is finished.')


    