## Author: Lisa Wallner
# Description: This Python script creates multiple summaries and README's for the provided cleaned source code from 201 GitHub repositories.
# Different prompts for the summary and the README creation are sent to an LLM via the Snowflake API and the results are stored in JSON files.
# Dependencies:
# - data/df_repos_counts_filtered.json
# - data/input_readme_data/

# Hint: If lines are created with support of a Large Language Model or the code is taken from another source, you find following hint at the end of the line:
#       (generated with Microsoft Copilot) or (source: link_to_source)

import os # package for using operating system
from dotenv import load_dotenv
from snowflake.snowpark.session import Session # package for building and using Snowflake sessions
# from snowflake.cortex import Complete
from transformers import AutoTokenizer # package to select the fitting tokenizer for a pretrained model
from huggingface_hub import login # package for login and identifying to Huggingface
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
        with open('../data/helper/repos_processed.json', 'r') as file: # open and load documentation file which contains information about previous processed repositories
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


def write_sub_summary_prompt(repo_name, input_txt, sub_summary_num, total_num_of_prompts):
    '''
    Function which writes the subsummary prompt for a GitHub repository.

    Args:
        repo_name: The name of the GitHub repository.
        input_txt: The source code of the GitHup repository as string.
        sub_summary_num: Number of subsummary.
        total_num_of_prompts: Total number of all all summaries.

    Return:
        prompt_sub_summary
    '''
    prompt_sub_summary = f'''
        You are acting as a software development expert for the following GitHub repository "{repo_name}".
        Your task is to summarize the given source code string "{input_txt}" in natural language, so a specialist is able to understand
        the purpose of the repository. This sourcecode is part {sub_summary_num} from {total_num_of_prompts}. 
        Note that you will not receive the full code because it will expand your maximum number of input tokens.
        Identify its purpose, key functions, main components and dependencies. Focus on the overall architecture and structure 
        rather than line-by-line details. Do not add any comments, recommendations or improvement suggestions, but concentrate on the summary. 
        Present the summary in a clear and concise language. 
        You are not allowed to add any small talk.
    ''' 
    
    return prompt_sub_summary


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
        Use the provided summary: "{summary_txt}", the license: "{license}" and the given requirements: "{requirements}".
        If the license and requirements are "None", try to find the missing content in the provided summary.
        The README file should contain information about what the project does, why it is useful, how users 
        can get started, where they can get help, and how to maintain and contribute to the project.
        If you don't know the answer, add a hint following this style […]. 
        You're not allowed to create made-up content to fill gaps, and or add additional paragraphs.

        Use the following Markdown template and fill in each paragraph. 

        ## Title

        ## Description

        ## Installation

        ## Usage

        ## Contributing

        ## License

        Do not include any sensitive data like names or emails. Keep the output clean, structured and well-formated using Markdown. 
        You are not allowed to add any small talk.
    '''

    return prompt_readme


def write_readme_prompt_from_subsummaries(repo_name, repo_owner, summary_txt, license, requirements):
    '''
    Function which writes the README prompt for a GitHub repository using the given summary (combined subsummaries), license and requirements.

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
        Use the provided subsummaries which are combined in one summary: "{summary_txt}", the license: "{license}" and the given requirements: "{requirements}".
        If the license and requirements are "None", try to find the missing content in the provided summary.
        The README file should contain information about what the project does, why it is useful, how users 
        can get started, where they can get help, and how to maintain and contribute to the project.
        If you don't know the answer, add a hint following this style […]. 
        You're not allowed to create made-up content to fill gaps, and or add additional paragraphs.

        Use the following Markdown template and fill in each paragraph. 

        ## Title

        ## Description

        ## Installation

        ## Usage

        ## Contributing

        ## License

        Do not include any sensitive data like names or emails. Keep the output clean, structured and well-formated using Markdown. 
        You are not allowed to add any small talk.
    '''

    return prompt_readme


def guess_tokens(num_of_chars):
    '''
    Function to guess the number of input tokens of the provided input for the LLM.
    '''
    num_of_tokens = math.floor(num_of_chars / 4) # estimation 4 characters per token
    num_of_tokens += 100 # Snowflake needs additional tokens for processing. The number of addtional tokens is not specified so this value is a guess.
    # see helper_count_tokens.ipynb (https://docs.snowflake.com/en/sql-reference/functions/count_tokens-snowflake-cortex)

    print(f'Number of guessed tokens for current repo: {num_of_tokens} (including addtional guess for Snowflake tokens)')
    return num_of_tokens


def send_query(prompt, type):
    if type == 'summary':
        model_params = model_summary_params
    elif type == 'readme':
        model_params = model_readme_params

    try:
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
        response = snowflake_session.sql(query, params=[model, prompt, model_params['temperature'], model_params['max_tokens']]).collect()
        #response = snowflake_session.sql(query).collect()
        res = json.loads(response[0]['RESPONSE'])
        message = res['choices'][0]['messages']
        total_tokens = res['usage']['total_tokens']
        completion_tokens = res['usage']['completion_tokens']
        prompt_tokens = res['usage']['prompt_tokens']

        print(f'SQL query for executing the {type} prompt was successful.')

        if type == 'summary':
            return message, total_tokens
        elif type == 'readme':
            return message, total_tokens, completion_tokens, prompt_tokens
        
    except Exception as e:
        print(f'Error for executing SQL statement: {e}')


def create_subprompts(prompt):
    max_tokens = 120000 # max number of tokens is 128000, but Snowflake requieres tokens for processing
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B")
    tokenized_prompt = tokenizer.encode(prompt)
    
    chunks = [tokenized_prompt[i:i+max_tokens] for i in range(0, len(tokenized_prompt), max_tokens)] # (generated with Microsoft Copilot)

    return [tokenizer.decode(chunk) for chunk in chunks] # (generated with Microsoft Copilot)


def write_json(repo_owner, repo_name, summary_list, readme, readme_total_tokens, readme_completion_tokens, readme_prompt_tokens):
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

    with open(f'../data/output_readme_data/{repo_owner}_{repo_name}_output.json', 'w') as file:
        json.dump(tmp_json, file)


def write_preprocessed_repo(repo_owner, repo_name):
    path = '../data/helper/repos_processed.json'
    try:
        with open(path, 'r') as file:
            data_list = json.load(file)
    except json.JSONDecodeError:
        data_list = []

    new_entry = [repo_owner, repo_name]
    data_list.append(new_entry)

    with open(path, 'w') as file:
        json.dump(data_list, file)


def check_repo_for_subprompts(repo_owner, repo_name):
    directory = '../data/tmp_output_data/'
    file_to_check = f'{repo_owner}_{repo_name}_tmp_output.json'

    if file_to_check in os.listdir(directory):
        print(f'Repo "{repo_name} is partly processed. Further works will continue.')
        return True
    else:
        return False
    

# load .env file
load_dotenv(override=True)

# log to huggingface
HF_TOKEN = os.environ['HUGGINGFACE']
login(HF_TOKEN)

# set up connection parameters for Snowflake connection
connection_params = {
    "account": os.environ['SNOWFLAKE_ACCOUNT'],
    "user": os.environ['SNOWFLAKE_USER'],
    "password": os.environ['SNOWFLAKE_USER_PASSWORD'],
    "role": 'ACCOUNTADMIN',
    "warehouse": 'COMPUTE_WH',
    'paramstyle': 'qmark'
}

# build Snowflake session with connection parameters
snowflake_session = Session.builder.configs(connection_params).create()
print('Snowflake sessions is build.')
print('---------------------------------------------')

# # define llm for summary
# # characters_per_token: 3.99 -->  3.9 mio characters per day
# # number of input tokens: 128,000
# # number of output tokens: 8,192
model = 'llama3.1-8b'
model_summary_params = {
   'temperature': 0, # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex --> Internetrecherche hat keine anderen Empfehlungen ergeben
   # 'top_p': # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex
    'max_tokens': 4000
}

model_readme_params = {
   'temperature': 0.1, # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex --> Internetrecherche hat keine anderen Empfehlungen ergeben
   # 'top_p': # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex
    'max_tokens': 6000
}

print('Model parameters are defined.')
print('---------------------------------------------')

# load json with filtered repository
# the summary and readme creation should begin with the repository which contains the smallest number of characters
loaded_data = open_json(path='../data/df_repos_counts_filtered.json')
df = pd.DataFrame(loaded_data)
print('Dataframe is created.')
print('---------------------------------------------')
repo_list = [(row.repo_owner, row.repo_name, row.source_code_cleaned_comments) for row in df.itertuples()]

num_of_all_tokens = 0 # new day --> 0
#  cnt = 0 # for testing
flag_break_loops = False # flag to break all loops, if number of subprompts is to big to process on one day

for i in repo_list:
    # if cnt >= 1: # for testing
    #     break
    if num_of_all_tokens >= 5200000: # 1 credit / 0.19 million tokens per credit --> 5.26 million tokens per day
            print('Number of tokens for daily processing reached. Continue at the next day.')
            print('---------------------------------------------')
            break

    if not check_repo_processed(repo_owner=i[0], repo_name=i[1]): 
        print(f'Repository "{i[1]}" will be processed.')
        repo_name = i[1]
        repo_owner = i[0]
        num_of_chars = i[2]
        repo_data = open_json(path=f'../data/input_readme_data/{repo_owner}_{repo_name}.json')
        source_code_cleaned_comments = repo_data['source_code_cleaned_comments']
        license = repo_data['license']
        requirements = repo_data['requirements']

        prompt_summary = write_summary_prompt(repo_name=repo_name, input_txt=source_code_cleaned_comments)
        print(f'Summary prompt for "{repo_name}" is created.')

        guess_of_tokens = guess_tokens(num_of_chars=len(prompt_summary))
        print(f'guess_of_tokens: {guess_of_tokens}')
        
        summary_list = []

        if guess_of_tokens < 126000:
            # prompt_summary = write_summary_prompt(repo_name=repo_name, input_txt=source_code_cleaned_comments)
            # print(f'Summary prompt for "{repo_name}" is created.')
            summary, summary_tokens = send_query(prompt=prompt_summary, type='summary')
            summary_list.append(summary)

            prompt_readme = write_readme_prompt(repo_name=repo_name, repo_owner=repo_owner, summary_txt=summary, license=license, requirements=requirements)
            print(f'README prompt for "{repo_name}" is created.')
            readme, readme_tokens, readme_completion_tokens, readme_prompt_tokens = send_query(prompt=prompt_readme, type='readme')

            write_json(repo_owner=repo_owner, repo_name=repo_name, summary_list=summary_list, readme=readme, readme_total_tokens=readme_tokens, readme_completion_tokens=readme_completion_tokens, readme_prompt_tokens=readme_prompt_tokens)
            write_preprocessed_repo(repo_owner=repo_owner, repo_name=repo_name)
            print(f'Summary and README for repository: "{repo_name}" from "{repo_owner}" successfully created.')

            num_of_all_tokens += summary_tokens
            num_of_all_tokens += readme_tokens
            print('---------------------------------------------')
            print(f'Number of processed tokens: {num_of_all_tokens}')
            # cnt += 1 # for testing
            

        else:
            print(f'Number of tokens of repository: "{repo_name}" to big to preprocess in single query. Subprompts are requiered.')

            if check_repo_for_subprompts(repo_owner=repo_owner, repo_name=repo_name):
                with open(f'../data/tmp_output_data/{repo_owner}_{repo_name}_tmp_output.json', 'r') as file:
                    loaded_data = json.load(file)

                summary_list = loaded_data['summary_list']
                processed_sub_prompts = loaded_data['processed_sub_prompts'] + 1
                sub_prompts = loaded_data['remaining_sub_prompts']
                total_num_of_prompts = loaded_data['total_num_of_prompts']
            else: 
                sub_prompts = create_subprompts(source_code_cleaned_comments) # list with chunks 
                total_num_of_prompts = len(sub_prompts)
                processed_sub_prompts = 1
        
            for prompt in sub_prompts:
                sub_prompt = prompt.replace('<|begin_of_text|>\n', '').replace('<|end_of_text|>\n', '')

                prompt_sub_summary = write_sub_summary_prompt(repo_name=repo_name, input_txt=sub_prompt, sub_summary_num=processed_sub_prompts, total_num_of_prompts=total_num_of_prompts )
                sub_summary, sub_summary_tokens = send_query(prompt_sub_summary, type='summary')
                
                tmp_json = {
                    f'summary_{processed_sub_prompts}': sub_summary,
                }

                num_of_all_tokens += sub_summary_tokens
                summary_list.append(tmp_json)
                processed_sub_prompts += 1

                if num_of_all_tokens >= 5200000:
                    tmp_json = {
                        'summary_list': summary_list,
                        'remaining_sub_prompts': sub_prompts[processed_sub_prompts -2:],
                        'processed_sub_prompts': processed_sub_prompts -1,
                        'total_num_of_prompts': total_num_of_prompts
                    }

                    with open(f'../data/tmp_output_data/{repo_owner}_{repo_name}_tmp_output.json', 'w') as file:
                        json.dump(tmp_json, file)

                    flag_break_loops = True
                    print('---------------------------------------------')
                    print('Flag to break all loops is set to True.')
                    print('Current list with summaries is saved for further processing.')
                    break
                

            if flag_break_loops == True:
                break

            tmp_list = [list(d.values())[0] for d in summary_list] 
            summary = ''.join(tmp_list)

            prompt_readme = write_readme_prompt_from_subsummaries(repo_name=repo_name, repo_owner=repo_owner, summary_txt=summary, license=license, requirements=requirements)
            readme, readme_tokens, readme_completion_tokens, readme_prompt_tokens = send_query(prompt=prompt_readme, type='readme')

            write_json(repo_owner=repo_owner, repo_name=repo_name, summary_list=summary_list, readme=readme, readme_total_tokens=readme_tokens, readme_completion_tokens=readme_completion_tokens, readme_prompt_tokens=readme_prompt_tokens)
            write_preprocessed_repo(repo_owner=repo_owner, repo_name=repo_name)

            print(f'Summary and README for repository: "{repo_name}" from "{repo_owner}" successfully created.')

            file_path = f'../data/tmp_output_data/{repo_owner}_{repo_name}_tmp_output.json'
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f'Temporary file {file_path} has been deleted.')
        
            num_of_all_tokens += readme_tokens
            print('---------------------------------------------')
            print(f'Number of processed tokens: {num_of_all_tokens}')
            # cnt += 1 # for testing

        print('---------------------------------------------')
    else:
        continue
    
snowflake_session.close()
print('---------------------------------------------')
print('Snowflake session is closed.')
