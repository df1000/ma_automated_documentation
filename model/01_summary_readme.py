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
        if type == 'summary':
            return message, total_tokens
        elif type == 'readme':
            return message, total_tokens, completion_tokens, prompt_tokens
        
    except Exception as e: # raise exception if SQL query was not successful
        print(f'Error for executing SQL statement: {e}')


def tokenize_text(txt):
    '''
    Function creates multiple chunks from given text to prevent limits for input tokens of choosed LLM.

    Args:
        prompt: Input which should be tokenized.
    
    Return:
        decoded_chunks
    '''
    max_tokens = 120000 # max number of tokens is 128000, but Snowflake requieres tokens for processing (see estimate_tokens())
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-8B") # load Autotokenizer.from_pretrained() from transformers with llm specification
    tokenized_txt = tokenizer.encode(txt) # encode txt into a list of tokens

    # iterates over tokenized_txt and split content into smaller chunks (each chunks contains a max. of 120000 tokens)
    # start at i = 0 and get a chunk until max_tokens (stepsize) from tokenized_prompt
    # next chunk --> previous chunk + max_tokens
    chunks = [tokenized_txt[i:i+max_tokens] for i in range(0, len(tokenized_txt), max_tokens)] # (generated with Microsoft Copilot)
    decoded_chunks = [tokenizer.decode(chunk) for chunk in chunks] # decode each chunk to text # (generated with Microsoft Copilot)
    
    return decoded_chunks


def create_chunk_list(input_txt):
    '''
    Function creates creates list with multiple chunks from the provided source code.

    Args:
        input_txt: A string with source code.

    Returns:
        chunk_list_cleaned
    '''
    max_sequence_length = 131072 # value was identified during errors with AutoTokenizer
    # list comprehension to iterate over input_txt and create elements which fit to max_sqeuence_length
    # range() --> start: 0, end: len(input_txt), stepsize: max_sequence_length
    # elements are sliced based on the given index range (which is controlled with range()) and max_sequence_length
    input_sequences = [input_txt[i:i+max_sequence_length] for i in range(0, len(input_txt), max_sequence_length)]
    chunk_list = [] # empty list to save chunks

    for sequence in input_sequences: # iterate through all sequences in input_sequences
        sequence_chunk = tokenize_text(sequence) # call tokenize_text() for each sequence
        chunk_list.append(sequence_chunk) # append decoded sequence_chunk to chunk_list
    
    print(f'Tokenization for {repo_name} is finished.')
    chunk_list_cleaned = [''.join(i).replace('<|begin_of_text|>', '') for i in chunk_list] # remove ''<|begin_of_text|>' sequence
    print(f'Repo needs {len(chunk_list_cleaned)} subsummaries.')

    return chunk_list_cleaned


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

    with open(f'../data/output_readme_data/{repo_owner}_{repo_name}_output.json', 'w') as file: # create new JSON file for GitHub repository
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
    path = '../data/helper/repos_processed.json' # path to documentation file
    try: # try to open documentation file
        with open(path, 'r') as file: # open and load file
            data_list = json.load(file) # save loaded content in data_list
    except json.JSONDecodeError: # raise exception if loaded file is empty
        data_list = [] # create new empty list

    new_entry = [repo_owner, repo_name] # creat new sublist for data_list containing repo_owner & repo_name of processed repository
    data_list.append(new_entry) # append new_entry to data_list

    with open(path, 'w') as file: # write processed data_list to documentation file
        json.dump(data_list, file)


def check_repo_for_subprompts(repo_owner, repo_name):
    '''
    Function to check whether the current Github repository is being processed.

    Args:
        repo_owner: The name of the GitHub repository owner.
        repo_name: The name of the GitHub repository.

    Return:
        Boolean
    '''
    directory = '../data/tmp_output_data/' # path to directory which contains temporary documentation file
    file_to_check = f'{repo_owner}_{repo_name}_tmp_output.json' # variable specifing the file

    if file_to_check in os.listdir(directory): # check if file_to_check is in directory
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

# # define llm for summary
# # characters_per_token: 3.99 -->  3.9 mio characters per day
# # number of input tokens: 128,000
# # number of output tokens: 8,192
model = 'llama3.1-8b'
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
#cnt = 0 # for testing
flag_break_loops = False # flag to break all loops, if number of subprompts is to big to process on one day

for i in repo_list: # iterate through all entries in repo_list --> each tuple represent a GitHub repository
    # if cnt >= 1: # for testing
    #     break
    if num_of_all_tokens >= 5200000: # 1 credit / 0.19 million tokens per credit --> 5.26 million tokens per day
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
            # prompt_summary = write_summary_prompt(repo_name=repo_name, input_txt=source_code_cleaned_comments)
            # print(f'Summary prompt for "{repo_name}" is created.')
            summary, summary_tokens = send_query(prompt=prompt_summary, type='summary') # call send_query() to create summary for repository
            summary_list.append(summary) # append summary to summary_list

            prompt_readme = write_readme_prompt(repo_name=repo_name, repo_owner=repo_owner, summary_txt=summary, license=license, requirements=requirements) # call write_readme_prompt()
            print(f'README prompt for "{repo_name}" is created.')
            readme, readme_tokens, readme_completion_tokens, readme_prompt_tokens = send_query(prompt=prompt_readme, type='readme') # call send_query() to create README for repository

            write_json(repo_owner=repo_owner, repo_name=repo_name, summary_list=summary_list, readme=readme, readme_total_tokens=readme_tokens, readme_completion_tokens=readme_completion_tokens, readme_prompt_tokens=readme_prompt_tokens) # call write_json()
            write_postprocessed_repo(repo_owner=repo_owner, repo_name=repo_name) # call write postprocessed_repo() to document progress
            print(f'Summary and README for repository: "{repo_name}" from "{repo_owner}" successfully created.')

            num_of_all_tokens += summary_tokens # increase num_of_all_tokens by summary_tokens
            num_of_all_tokens += readme_tokens # increase num_of_all_tokens by readme_tokens
            print('---------------------------------------------')
            print(f'Number of processed tokens: {num_of_all_tokens}')
            #cnt += 1 # for testing

        else: # if guess_of_tokens is not smaller then 126,000 --> subsummaries are required
            print(f'Number of tokens of repository: "{repo_name}" to big to preprocess in single query. Subprompts are requiered.')

            if check_repo_for_subprompts(repo_owner=repo_owner, repo_name=repo_name): # call check_repo_for_subprompts() to check if the process of summary generation already started (e.g. yesterday)
                with open(f'../data/tmp_output_data/{repo_owner}_{repo_name}_tmp_output.json', 'r') as file: # open and load temporary file of current repository
                    loaded_data = json.load(file) # save file in loaded_data
                
                # save documented progress in the following variables
                summary_list = loaded_data['summary_list']
                processed_sub_prompts = loaded_data['processed_sub_prompts'] + 1 # increase number of processed_sub_prompts to track further progress (step 2 --> see line 529)
                sub_prompts = loaded_data['remaining_sub_prompts'] # these are the remaing subprompts!!!!
                total_num_of_prompts = loaded_data['total_num_of_prompts']

            else: # if the process of summary generation hasn't started yet
                chunk_list = create_chunk_list(source_code_cleaned_comments) # call create_subprompts() --> list with chunks of source code of repository
                total_num_of_prompts = len(chunk_list) # get number of necessary subprompts 
                processed_sub_prompts = 1 # set variable to 1 --> first subprompt
        
            for chunk in chunk_list: # iterate over all prompts in the list sub_prompts
                prompt_sub_summary = write_sub_summary_prompt(repo_name=repo_name, input_txt=chunk, sub_summary_num=processed_sub_prompts, total_num_of_prompts=total_num_of_prompts) # call write_sub_summary_prompt() 
                sub_summary, sub_summary_tokens = send_query(prompt_sub_summary, type='summary') # call send_query() to create subsummary for repository
                
                # temporary JSON object with current sub_summary
                tmp_json = {
                    f'summary_{processed_sub_prompts}': sub_summary,
                }

                num_of_all_tokens += sub_summary_tokens # increase num_of_all_tokens by sub_summary_tokens
                summary_list.append(tmp_json) # append tmp_json to summary_list
                processed_sub_prompts += 1 # increase processed_sub_prompts by 1 (step 1 --> see line 530)

                if num_of_all_tokens >= 5200000: # if num_of_all_tokens >= 5200000 the loop should break to prevent computing errors from Snowflake
                    # create tmp_json to document current state of processed subsummaries
                    tmp_json = {
                        'summary_list': summary_list, # list with processed summaries
                        'remaining_sub_prompts': chunk_list[processed_sub_prompts -2:], # sub_prompts which aren't processed yet --> -2 to get to the level before 2 steps
                        'processed_sub_prompts': processed_sub_prompts -1, # sub_prompts which are already processed --> -1 to get to the level before 1 step
                        'total_num_of_prompts': total_num_of_prompts # total number of necessary sub_prompts
                    }

                    with open(f'../data/tmp_output_data/{repo_owner}_{repo_name}_tmp_output.json', 'w') as file: # save current progress of subprompt creation for repository in JSON file
                        json.dump(tmp_json, file) # write tmp_json to file

                    flag_break_loops = True # set flag from False to True so sub_prompts loop will break
                    print('---------------------------------------------')
                    print('Flag to break all loops is set to True.')
                    print('Current list with summaries is saved for further processing.')
                    break
                

            if flag_break_loops == True: # check flag if True break repo_list loop
                break

            tmp_list = [list(d.values())[0] for d in summary_list] # iterate of each JSON object in summary_list (list with sub_summaries saved in dicts), convert it to a list, extract the first item (the summary) and save it in tmp_list
            summary = ''.join(tmp_list) # join all elements of tmp_list to one string and save it in summary

            prompt_readme = write_readme_prompt_from_subsummaries(repo_name=repo_name, repo_owner=repo_owner, summary_txt=summary, license=license, requirements=requirements) # call write_readmeprompt_from_subsummaries()
            readme, readme_tokens, readme_completion_tokens, readme_prompt_tokens = send_query(prompt=prompt_readme, type='readme') # call send_query() to create README for repository

            write_json(repo_owner=repo_owner, repo_name=repo_name, summary_list=summary_list, readme=readme, readme_total_tokens=readme_tokens, readme_completion_tokens=readme_completion_tokens, readme_prompt_tokens=readme_prompt_tokens)  # call write_json()
            write_postprocessed_repo(repo_owner=repo_owner, repo_name=repo_name) # call write_postprocessed_repo() to document progress

            print(f'Summary and README for repository: "{repo_name}" from "{repo_owner}" successfully created.')

            file_path = f'../data/tmp_output_data/{repo_owner}_{repo_name}_tmp_output.json' # set file path to temporary JSON file which contains the subsummaries
            if os.path.exists(file_path): # check if file_path exits
                os.remove(file_path) # remove the file_path
                print(f'Temporary file {file_path} has been deleted.')
        
            num_of_all_tokens += readme_tokens # increase num_of_all_tokens by readme_tokens
            print('---------------------------------------------')
            print(f'Number of processed tokens: {num_of_all_tokens}')
            #cnt += 1 # for testing

        print('---------------------------------------------')
    else: # if current repository is already processed continue with the next one
        continue
    
snowflake_session.close() # close snowflake session
print('---------------------------------------------')
print('Snowflake session is closed.')
