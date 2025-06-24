## Author: Lisa Wallner
# Description: This Python script creates multiple summaries and README's for the provided cleaned source code from multiple GitHub repositories. This is the code for the second approach - the prompt has some small modifications.
# Different prompts for the summary and the README creation are sent to an LLM via the Snowflake API and the results are stored in JSON files.
# Dependencies:
# - data/df_repos_counts_filtered.json
# - data/input_readme_data/

# Hint: If lines are created with support of a Large Language Model or the code is taken from another source, you find following hint at the end of the line:
#       (generated with Microsoft Copilot) or (source: link_to_source)

import os # package for using operating system
from dotenv import load_dotenv
from snowflake.snowpark.session import Session # package for building and using Snowflake sessions
import pandas as pd # package for data manipulation
import json # package to work with .json
import math # package for mathematical operations


def open_json(path):
    '''
    Function which opens and read a JSON file.

    Args:
        path: Path to JSON file.

    Return:
        loaded_data or {}
    '''
    try: # try to open file
        with open(path, 'r') as file: # open and load JSON file
            loaded_data = json.load(file) 
        return loaded_data # save loaded content in variable loaded_data
    except json.decoder.JSONDecodeError: # raise exception if JSONDecodeError --> file is empty
        return {}


def check_repo_processed(repo_owner, repo_name):
    '''
    Function which checks if a GitHub repository is already processed.

    Args:
        repo_owner: The name of the GitHub repository owner.
        repo_name: The name of the GitHub repository.
    
    Return:
        Boolean
    '''
    try: # try to open documentation file
        repo_to_check = [repo_owner, repo_name] # list with two values --> repo to check
        path = '../data/helper/repos_processed_lama_mod.json' # path for first try with llama3.1-8b
        # path = '../data/helper/repos_processed_jamba_mod.json' # path for second try with jamba-1.5-mini
        with open(path, 'r') as file: # open and load documentation file which contains information about previous processed repositories
            data_list = json.load(file) # save loaded content in variable data_list
    except json.JSONDecodeError: # raise exception if JSONDecodeError --> documentation file is empty
        data_list = [] # create new empty list

    if repo_to_check in data_list: # check if repository is already processed
        print(f'Repo "{repo_name}" from "{repo_owner} is already processed.')
        return True
    else: 
        return False


def write_summary_prompt(repo_name, input_txt):
    '''
    Function which writes the summary prompt for a GitHub repository.

    Args:
        repo_name: The name of the GitHub repository.
        input_txt: The source code of the GitHup repository as string.

    Return:
        prompt_summary
    '''
    prompt_summary = f'''
        You are acting as a software development expert for the following GitHub repository "{repo_name}".
        Your task is to summarize the given source code string "{input_txt}" in natural language, so a specialist is able to understand
        the purpose of the repository.
        Identify its purpose, key functions, main components and dependencies. Focus on the overall architecture and structure 
        rather than line-by-line details. Do not add any recommendations or improvement suggestions, but concentrate on the summary. 
        Present the summary in a clear and concise language.
        You are not allowed to add any small talk. 
    ''' 

    return prompt_summary


def write_readme_prompt(repo_name, repo_owner, summary_txt, license, requirements):
    '''
    Function which writes the README prompt for a GitHub repository using the given summary, license and requirements.

    Args:
        repo_name: The name of the GitHub repository.
        repo_onwer: The name of the GitHub repository owner.
        summary_txt: The summary of the GitHub repository source code as string.
        license: The license text as string.
        requirements: The requirements as string.

    Return:
        prompt_readme
    '''
    prompt_readme = f'''
        You are acting as a software development expert for the following GitHub repository: "{repo_name}" from the owner "{repo_owner}". 
        Your task is to create a README for the repository in Markdown format. 
        Use the provided summary: "{summary_txt}" and the license: "{license}".
        If the license and requirements are "None", try to find the missing content in the provided summary.
        The README file should contain information about what the project does, why it is useful, how users 
        can get started, where they can get help, and how to maintain and contribute to the project.
        If you don't know the answer, add a hint following this style […]. 
        You're not allowed to create made-up content to fill gaps, and or add additional paragraphs.

        Use the following Markdown template and fill in each paragraph. 

        # Title

        ## Description

        ## Installation

        ## Usage

        ## Contributing

        ## License

        Keep the output clean, structured and well-formated using Markdown. 
        You are not allowed to add any small talk.
    '''

    return prompt_readme


# Snowflake limits the number of processing tokens per day in the free trail (1 credit for AI functions per day). https://docs.snowflake.com/en/user-guide/admin-trial-account
# There are SQL statements which calcualate the number of tokens but these compuations also requiere credits.
# To save credits because they are needed for the summary and README creation the following function was build.
# Dependencies: helper_count_tokens.ipynb
def estimate_tokens(num_of_chars):
    '''
    Function to estimate the number of input tokens from the given number of characters.

    Args:
        num_of_chars: Number of characters of the input text.
    
    Retrun:
        num_of_tokens
    '''
    # see helper_count_tokens.ipynb for derivation of value 4
    num_of_tokens = math.floor(num_of_chars / 4) # divide num_of_chars through and get largest integer less or equal to x 4 # estimation 4 characters per token
    num_of_tokens += 100 # Snowflake needs additional tokens for processing. The number of addtional tokens is not specified so this value is a guess. (https://docs.snowflake.com/en/sql-reference/functions/count_tokens-snowflake-cortex)

    print(f'Number of guessed tokens for current repo: {num_of_tokens} (including addtional guess for Snowflake tokens)')
    return num_of_tokens


def send_query(prompt, type):
    '''
    Function which sends a SQL query to Snowflake based on given parameters, collect and return the results.

    Args:
        prompt: Specified prompt which should be processed by the SQL snowflake.cortex.complete() function.
        type: A string specificing the prompt parameters.

    Return:
        message, total_tokens, completion_tokens (optional), prompt_tokens (optional)
    '''
    # check value of variable type and set model_params for README or summary creation
    if type == 'summary': 
        model_params = model_summary_params
    elif type == 'readme':
        model_params = model_readme_params

    try: # try to create and execute sql query
        # snowflake.cortex.complete() --> calls llm to generate a response based on given prompt and parameter
        # ? --> placeholder for variables (model, prompt, model_params['temperature'], model_params['max_tokens'])
        query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE( 
                ?,
                [
                    {{
                        'role': 'user', 
                        'content': ?
                    }}
                ],
                {{
                    'temperature': ?,
                    'max_tokens':  ?
                }} 
            ) AS response
        """
        # query parameters
        # model --> llm model
        # prompt --> input prompt with instructions for llm
        # model_params['temperature'] --> controll randomness in llm response
        # model_params['max_tokens'] --> limit llm response length
        # sql().collect() --> execute sql statement and return a DataFrame (no Pandas dataframe) as list of row objects https://docs.snowflake.com/en/developer-guide/snowpark/reference/python/latest/snowpark/api/snowflake.snowpark.DataFrame.collect#snowflake.snowpark.DataFrame.collect
        response = snowflake_session.sql(query, params=[model, prompt, model_params['temperature'], model_params['max_tokens']]).collect()
        res = json.loads(response[0]['RESPONSE']) # load response as json object and save it in 'res'
        # split 'res' parts and save them into multiple variabels
        message = res['choices'][0]['messages'] # https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex
        total_tokens = res['usage']['total_tokens'] # total number of tokens consumed, which is the sum of completion_tokens & prompt_tokens
        completion_tokens = res['usage']['completion_tokens'] # number of tokens in genearted response (Anzahl der Outputtokens, also wie lange die Anwort vom LLM ist)
        prompt_tokens = res['usage']['prompt_tokens'] # number of tokens in the prompt

        print(f'SQL query for executing the {type} prompt was successful.')

        # based on type return specific results
        if type == 'readme':
            return message, total_tokens, completion_tokens, prompt_tokens
        else: 
            return message, total_tokens
        
    except Exception as e: # raise exception if SQL query was not successful
        print(f'Error for executing SQL statement: {e}')


def write_json(repo_owner, repo_name, summary_list, readme, readme_total_tokens, readme_completion_tokens, readme_prompt_tokens):
    '''
    Function to write and save a JSON file containing data of a GitHub repository for later evaluation.

    Args:
        repo_owner: The name of the GitHub repository owner.
        repo_name: The name of the GitHub repository.
        summary_list: A list containing one or multiple summaries of the GitHub repository source code.
        readme: A README for the specific GitHub repository as string.
        readme_total_tokens: Number of total processed tokens (completion & prompt) for the README creation.
        readme_completion_tokens: Number of processed completion tokens for the README creation.
        readme_prompt_tokens: Number of processed prompt tokens for the README creation.

    Return:
        None
    '''
    # template for JSON structure
    tmp_json = {
        'repo_owner': repo_owner,
        'repo_name': repo_name,
        'summaries': summary_list,
        'readme': readme,
        'readme_tokens': {
            'total_tokens': readme_total_tokens,
            'completion_tokens': readme_completion_tokens,
            'prompt_tokens':readme_prompt_tokens
        }
    }

    path = f'../data/output_readme_data_lama_mod/{repo_owner}_{repo_name}_output_mod.json' # path for first try with lama
    # path = f'../data/output_readme_data_jamba_mod/{repo_owner}_{repo_name}_output_mod.json' # path for second try with jamba-1.5-mini
    with open(path, 'w') as file: # create new JSON file for GitHub repository
        json.dump(tmp_json, file) # write tmp_json to new file


def write_postprocessed_repo(repo_owner, repo_name):
    '''
    Function which writes processed GitHub repository to a documentation file.

    Args:
        repo_owner: The name of the GitHub repository owner.
        repo_name: The name of the GitHub repository.

    Return:
        None
    '''
    path = '../data/helper/repos_processed_lama_mod.json' # path to documentation file
    # path = '../data/helper/repos_processed_jamba_mod.json' # path to documentation file for second try with jamba-1.5-mini
    try: # try to open documentation file
        with open(path, 'r') as file: # open and load file
            data_list = json.load(file) # save loaded content in data_list
    except json.JSONDecodeError: # raise exception if loaded file is empty
        data_list = [] # create new empty list

    new_entry = [repo_owner, repo_name] # creat new sublist for data_list containing repo_owner & repo_name of processed repository
    data_list.append(new_entry) # append new_entry to data_list

    with open(path, 'w') as file: # write processed data_list to documentation file
        json.dump(data_list, file)
    

# load .env file
load_dotenv(override=True)

# set up connection parameters for Snowflake connection
connection_params = {
    "account": os.environ['SNOWFLAKE_ACCOUNT'], # credentials
    "user": os.environ['SNOWFLAKE_USER'], # credentials
    "password": os.environ['SNOWFLAKE_USER_PASSWORD'], # credentials
    "role": 'SYSADMIN', # specifiy Snowflake role
    "warehouse": 'COMPUTE_WH', # choose warehouse for computation
    'paramstyle': 'qmark' # set parameter style --> ?
}

snowflake_session = Session.builder.configs(connection_params).create() # build Snowflake session with connection parameters
print('Snowflake sessions is build.')
print('---------------------------------------------')

# define llm for summary
# characters_per_token: 3.99 -->  3.9 mio characters per day
# number of input tokens: 128,000
# number of output tokens: 8,192
model = 'llama3.1-8b'
# characters_per_token: 3.78 -->  3.7 mio characters per day
# number of input tokens: 256,000
# number of output tokens: 8,192
# model = 'jamba-1.5-mini'
# specify llm parameters for summary creation
model_summary_params = {
   'temperature': 0, # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex --> Internetrecherche hat keine anderen Empfehlungen ergeben
   # 'top_p': # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex
    'max_tokens': 4000
}

# specify llm parameters for README creation
model_readme_params = {
   'temperature': 0.1, # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex --> Internetrecherche hat keine anderen Empfehlungen ergeben
   # 'top_p': # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex
    'max_tokens': 6000
}

print('Model parameters are defined.')
print('---------------------------------------------')


# the summary and readme creation should begin with the repository which contains the smallest number of characters
loaded_data = open_json(path='../data/df_repos_counts_filtered.json') # load json with filtered repository
df = pd.DataFrame(loaded_data) # create Pandas dataframe with loaded_data
print('Dataframe is created.')
print('---------------------------------------------')
# create repo_list from df, each row of the df is represented as tuple (repo_owner, repo_name, source_code_cleanded_comments) 
repo_list = [(row.repo_owner, row.repo_name, row.source_code_cleaned_comments) for row in df.itertuples()]

num_of_all_tokens = 0 # number of processed tokens # new day --> 0
cnt = 0 # for testing
flag_break_loops = False # flag to break all loops, if number of subprompts is to big to process on one day

for i in repo_list: # iterate through all entries in repo_list --> each tuple represent a GitHub repository
    if cnt >= 51: # for testing
        break
    if num_of_all_tokens >= 5200000: # 1 credit / 0.19 million tokens per credit --> 5.26 million tokens per day
    # if num_of_all_tokens >= 9000000: # for second try with jamba-1.5-mini --> 1 credit / 0.10 millionen tokens per credit --> 10 millionen tokens per day
            print('Number of tokens for daily processing reached. Continue at the next day.')
            print('---------------------------------------------')
            break # if num_of_all_tokens >= 5200000 the loop should bread to prevent computing errors from Snowflake

    if not check_repo_processed(repo_owner=i[0], repo_name=i[1]): # call check_repo_processed() for i (specific repository)
        print(f'Repository "{i[1]}" will be processed.')
        repo_name = i[1] # set repo_name to i[1]
        repo_owner = i[0] # set repo_owner to i[0]
        # num_of_chars = i[2] 
        repo_data = open_json(path=f'../data/input_readme_data/{repo_owner}_{repo_name}.json') # call open_json()
        source_code_cleaned_comments = repo_data['source_code_cleaned_comments'] # save cleaned repository source code in variable source_code_cleaned_comments
        license = repo_data['license'] # set license of repository
        requirements = repo_data['requirements'] # set license of repository

        prompt_summary = write_summary_prompt(repo_name=repo_name, input_txt=source_code_cleaned_comments) # call write_summary_prompt()
        print(f'Summary prompt for "{repo_name}" is created.')

        guess_of_tokens = estimate_tokens(num_of_chars=len(prompt_summary)) # call estimate_tokens()
        print(f'guess_of_tokens: {guess_of_tokens}')
        
        summary_list = [] # create empty list to save future generated summaries

        if guess_of_tokens < 120000: # check if guess_of_tokens is smaller then 120,000 
        # if guess_of_tokens < 200000: # for second try with jamba-1.5-mini
            summary, summary_tokens = send_query(prompt=prompt_summary, type='summary') # call send_query() to create summary for repository
            summary_list.append(summary) # append summary to summary_list

            prompt_readme = write_readme_prompt(repo_name=repo_name, repo_owner=repo_owner, summary_txt=summary, license=license, requirements=requirements) # call write_readme_prompt()
            print(f'README prompt for "{repo_name}" is created.')
            readme, readme_tokens, readme_completion_tokens, readme_prompt_tokens = send_query(prompt=prompt_readme, type='readme') # call send_query() to create README for repository

            write_json(repo_owner=repo_owner, repo_name=repo_name, summary_list=summary_list, readme=readme, readme_total_tokens=readme_tokens, readme_completion_tokens=readme_completion_tokens, readme_prompt_tokens=readme_prompt_tokens) # call write_json()
            write_postprocessed_repo(repo_owner=repo_owner, repo_name=repo_name) # call write postprocessed_repo() to document progress
            print(f'Summary and README for repository: "{repo_name}" from "{repo_owner}" successfully created. used model {model}')

            num_of_all_tokens += summary_tokens # increase num_of_all_tokens by summary_tokens
            num_of_all_tokens += readme_tokens # increase num_of_all_tokens by readme_tokens
            print('---------------------------------------------')
            print(f'Number of processed tokens: {num_of_all_tokens}')
            cnt += 1 # for testing

        else: # if guess_of_tokens is not smaller then 126,000 --> subsummaries are required
            print(f'Number of tokens of repository: "{repo_name}" to big to preprocess in single query. Subprompts are requiered.')

        print('---------------------------------------------')
    else: # if current repository is already processed continue with the next one
        continue

snowflake_session.close() # close snowflake session
print('---------------------------------------------')
print('Snowflake session is closed.')
