# Author: Lisa Wallner
# Description: In this Python script metadata of multiple GitHub repositories via the API will be requested. With this script the first
# request was executed to collect repositories with a star range from maximum number of stars ascending --> 1050 results.
# Further analysis are processed in the following scripts:
# - preprocessing/01_repos_metadata.ipynb
# - preprocessing/02_analyse_repos_metadata.ipynb
#
# Hint: If lines are created with support of a Large Language Model or the code is taken from another source, you find following hint at the end of the line:
#       (generated with Microsoft Copilot) or (source: link_to_source)


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

def get_response(page):
    # set url
    url_multiple_repos  = f'https://api.github.com/search/repositories?q=language:python&sort:asc&page={page}'
    # send request
    response = requests.request('GET', url=url_multiple_repos, headers=headers, data=payload)
    if response.status_code != 200:
        print(f'Error with response. Check out status_code {response.status_code}!')

        return page
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
    random_number = random.randint(2,8)
    time.sleep(random_number)


# https://api.github.com/search/repositories?q=language:python
# Link: <https://api.github.com/search/repositories?q=language%3Apython&page=2>; rel="next", <https://api.github.com/search/repositories?q=language%3Apython&page=34>; rel="last"
# beim responses via Postman habe ich die Info erhalten, das die nächtes page "2" ist und die letzte "34"
num_of_pages = 34
# empty list for page numbers with no response
pages_with_no_response = []


for page in range(0, num_of_pages+1):
    set_sleeper()    
    if get_response(page) == None:
        continue
    # add page with wrong response code to list
    pages_with_no_response.append(page)

if not pages_with_no_response:
    print(f'Response of all {num_of_pages} pages was saved into the directory data.') 
else:
    # temporary list to store pages with no response
    tmp_list = []
    # check pages with no response again
    for page in pages_with_no_response:
        set_sleeper()
        if get_response(page) is None:
            tmp_list.append(page)
            continue
        # add page with wrong response code to list
        pages_with_no_response.append(page)

if tmp_list is not None:
    pages_with_no_response = tmp_list
    # save list for later analysis
    with open(f'../data/helper/pages_with_wrong_response.json', 'w') as file:
        json.dump(pages_with_no_response, file)
else:
    print('Getting repository metadata is finished.')


    