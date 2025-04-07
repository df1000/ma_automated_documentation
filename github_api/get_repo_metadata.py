import requests
import json
from getpass import getpass
import pandas as pd
from datetime import datetime
import time

# set credentials
ACCESS_TOKEN = getpass()
payload = {}
headers = {
  'Accept': 'application/vnd.github+json',
  'X-GitHub-Api-Version': '2022-11-28',
  'Authorization': f'Bearer {ACCESS_TOKEN}'
}

# https://api.github.com/search/repositories?q=language:python
# Link: <https://api.github.com/search/repositories?q=language%3Apython&page=2>; rel="next", <https://api.github.com/search/repositories?q=language%3Apython&page=34>; rel="last"
# beim responses via Postman habe ich die Info erhalten, das die nächtes page "2" ist und die letzte "34"
num_of_pages = 34

for page in range(0, num_of_pages+1):
    # set sleeper
    time.sleep(3)
    # set url
    url_multiple_repos = f'https://api.github.com/search/repositories?q=language:python&page={page}'
    # send request
    response = requests.request('GET', url=url_multiple_repos, headers=headers, data=payload)
    if response.status_code != 200:
        print(f'Error with response. Check out status_code {response.status_code}!')
    else:
        # save response in variable 
        data = response.json()
        # set timestamp as str
        timestamp = datetime.now(tz=None).strftime('%Y-%m-%d_%H-%H-%S')
        # save data from response as json in data/
        with open(f'../data/{timestamp}multiple_github_repos_page_{page}.json', 'w') as file:
            json.dump(data, file)



    