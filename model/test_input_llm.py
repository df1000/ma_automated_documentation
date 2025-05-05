@sleep_and_retry
@limits(calls=10, period=ONE_MINUTE)
def check_repo_for_readme(repo_owner, repo_name):

    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/readme'
    response = requests.get(url, headers=HEADERS, data=PAYLOAD)
    if response.status_code == 404:
        print(f'Repo {repo_name} has no README.md.')
        return False
    elif response.status_code == 200:
        return True
    else:
        if response.status_code != 200:
            print(f'Error with response. Check out status_code {response.status_code}!')
            rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining'))
            if rate_limit_remaining <= 1:
                set_sleeper(61)
        return False
    



#     SELECT
#   SNOWFLAKE.CORTEX.COMPLETE(
#     'snowflake-llama-3.3-70b',
#     [{'role':'user','content':'create a short summary of the given python code. limit your output to the relevant parts and answer in natural language: @sleep_and_retry
# @limits(calls=10, period=ONE_MINUTE)
# def check_repo_for_readme(repo_owner, repo_name):

#     url = f''https://api.github.com/repos/{repo_owner}/{repo_name}/readme''
#     response = requests.get(url, headers=HEADERS, data=PAYLOAD)
#     if response.status_code == 404:
#         print(f''Repo {repo_name} has no README.md.'')
#         return False
#     elif response.status_code == 200:
#         return True
#     else:
#         if response.status_code != 200:
#             print(f''Error with response. Check out status_code {response.status_code}!'')
#             rate_limit_remaining = int(response.headers.get(''X-RateLimit-Remaining''))
#             if rate_limit_remaining <= 1:
#                 set_sleeper(61)
#         return False'}],
#     { }
#   );