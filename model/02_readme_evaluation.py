## Author: Lisa Wallner
# Description: This Python script creates the evaluations for the original and genearted README files of multiple GitHub repositories.
# Different prompts for evaluation (1 prompt for the generated README and 1 prompt for the original README) are sent to an LLM via the 
# Snowflake API and the results are stored in JSON files.
# Dependencies:
# - data/input_readme_data/

# Hint: If lines are created with support of a Large Language Model or the code is taken from another source, you find following hint at the end of the line:
#       (generated with Microsoft Copilot) or (source: link_to_source)

import pandas as pd
import os # package for using operating system
from dotenv import load_dotenv
from snowflake.snowpark.session import Session # package for building and using Snowflake sessions
import pandas as pd # package for data manipulation
import json # package to work with .json
import re # package tow work with Regex patterns

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
    

def check_readme_eval_processed(repo_owner, repo_name, model_type):
    '''
    Function which checks if a GitHub repository is already processed.

    Args:
        repo_owner: The name of the GitHub repository owner.
        repo_name: The name of the GitHub repository.
        model_type: Name of used LLM.
    
    Return:
        Boolean
    '''
    # check value of model_type to define path
    if model_type == 'llama3.1-8b': 
        # path = '../data/helper/helper_readme_eval_processed_m1_lama.json'
        path = '../data/helper/helper_readme_eval_processed_m1_jamba.json'
        # path = '../data/helper/helper_readme_eval_processed_m1_lama_mod.json'
        # path = '../data/helper/helper_readme_eval_processed_m1_jamba_mod.json'
    elif model_type == 'reka-flash':
        # path = '../data/helper/helper_readme_eval_processed_m2_lama.json'
        path = '../data/helper/helper_readme_eval_processed_m2_jamba.json'
        # path = '../data/helper/helper_readme_eval_processed_m2_lama_mod.json'
        # path = '../data/helper/helper_readme_eval_processed_m2_jamba_mod.json'
    elif model_type == 'jamba-1.5-mini':
        # path = '../data/helper/helper_readme_eval_processed_m3_lama.json'
        path = '../data/helper/helper_readme_eval_processed_m3_jamba.json'
        # path = '../data/helper/helper_readme_eval_processed_m3_lama_mod.json'
        # path = '../data/helper/helper_readme_eval_processed_m3_jamba_mod.json'

    try: # try to open documentation file
        repo_to_check = [repo_owner, repo_name] # list with two values --> repo to check
        with open(path, 'r') as file: # open and load documentation file which contains information about previous processed repositories
            data_list = json.load(file) # save loaded content in variable data_list
    except json.JSONDecodeError: # raise exception if JSONDecodeError --> documentation file is empty
        data_list = [] # create new empty list

    if repo_to_check in data_list: # check if repository is already processed
        print(f'Repo "{repo_name}" from "{repo_owner} is already processed.')
        return True
    else: 
        return False
    

def write_evaluation_prompt(repo_name, input_txt):
    '''
    Function which writes the evaluation prompt for a README.

    Args:
        repo_name: The name of the GitHub repository.
        input_txt: The README of the GitHup repository as string.

    Return:
        prompt_evaluation
    '''
    prompt_evaluation = f'''
    You are acting as a software development expert for the following GitHub repository "{repo_name}".
    Your task is to evaluate the following README of the repository/project based on the provided questions:
        - q1: What is the goal of the project?
        - q2: Why is the project useful?
        - q3: How can users get started with the project?
        - q4: Where can users get help with your project?
        - q5: Who maintains and contributes to the project?
    How well does the provided README offers answers to each question? Score each question on a scale from 1 to 5, 
    in which 1 means "insufficient", 2 "sufficienct", 3 "satisfactory", 4 "good" and 5 "very good". Provide your chosen score with a short explanation.
    A good indication of a high score is: 1) there is a section or paragraph where ab answer of the questions is clearly provided,
    2) the content of the README is clearly structured and understandable 3) that a developer who reads the README understands the purpose of the project.
    You're not allowed to skip a question or add any small talk!
    Structure your response in the following format:
    ###
    "q1": [
        ##"score": your_score##,
        ##"explanation": your_explanation##
        ]
    ###
    "q2": ...
    ###
    Here is the README to evaluate:
    {input_txt}
    ''' 

    return prompt_evaluation


def send_query(prompt_evaluation, model_type):
    '''
    Function which sends a SQL query to Snowflake based on given parameters, collect and return the results.

    Args:
        prompt: Specified prompt which should be processed by the SQL snowflake.cortex.complete() function.
        model_type: A string specificing the model parameters.

    Return:
        message, total_tokens, completion_tokens (optional), prompt_tokens (optional)
    '''
    # check value of model_type and set model_params for README or summary creation
    if model_type == 'llama3.1-8b': 
        model_params = model1_params
    elif model_type == 'reka-flash':
        model_params = model2_params
    elif model_type == 'jamba-1.5-mini': 
        model_params = model3_params

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
        response = snowflake_session.sql(query, params=[model_type, prompt_evaluation, model_params['temperature'], model_params['max_tokens']]).collect()
        res = json.loads(response[0]['RESPONSE']) # load response as json object and save it in 'res'
        # split 'res' parts and save them into multiple variabels
        message = res['choices'][0]['messages'] # https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex
        total_tokens = res['usage']['total_tokens'] # total number of tokens consumed, which is the sum of completion_tokens & prompt_tokens
        completion_tokens = res['usage']['completion_tokens'] # number of tokens in genearted response (Anzahl der Outputtokens, also wie lange die Anwort vom LLM ist)
        prompt_tokens = res['usage']['prompt_tokens'] # number of tokens in the prompt

        # values of tokens are saved in a dictonary for later analysis
        evaluation_tokens = {
            'total_tokens': total_tokens,
            'completion_tokens': completion_tokens,
            'prompt_tokens': prompt_tokens
        }

        print(f'SQL query for executing the evaluation prompt for model {model_type} was successful.')

        return message, evaluation_tokens, total_tokens
        
    except Exception as e: # raise exception if SQL query was not successful
        print(f'Error for executing SQL statement: {e}')


def write_json(model_type, repo_owner, repo_name, readme_original, evaluation_original, evaluation_original_tokens, evaluation_original_score, readme_generated, evaluation_generated, evaluation_generated_tokens, evaluation_generated_score):
    '''
    Function to write and save a JSON file containing the evaluation data for a GitHub repository README file.

    Args:
        model_type: 
        repo_owner: The name of the GitHub repository owner.
        repo_name: The name of the GitHub repository.
        readme_original: A dictionary with the evaluation data for the README file.
            readme: A README for the specific GitHub repository as string.
            evaluation: Evaluation of README as string.
            evaluation_tokens: Number of processed tokens for the README evaluation saved in a dictionary.
            score: Processed output of evaluation in structured format for later analysis.
        readme_generated: A dictionary with the evaluation data for the README file.
            readme: A README for the specific GitHub repository as string.
            evaluation: Evaluation of README as string.
            evaluation_tokens: Number of processed tokens for the README evaluation saved in a dictionary.
            score: Processed output of evaluation in structured format for later analysis.

    Return:
        None
    '''
    # template for JSON structure
    tmp_json = {
                "repo_owner": repo_owner,
                "repo_name": repo_name,
                "readme_original": {
                    "readme": readme_original,
                    "evaluation": evaluation_original,
                    "evaluation_tokens": evaluation_original_tokens,
                    "score": evaluation_original_score
                },
                "readme_genereated": {
                    "readme": readme_generated,
                    "evaluation": evaluation_generated,
                    "evaluation_tokens": evaluation_generated_tokens,
                    "score": evaluation_generated_score
                }
    }
    # check value of model_type to specify the directory for data saving
    if model_type == 'llama3.1-8b': 
        model_dir = 'model1'
    elif model_type == 'reka-flash':
        model_dir = 'model2'
    elif model_type == 'jamba-1.5-mini': 
        model_dir = 'model3'

    # path = f'../data/output_evaluation_data_lama/{model_dir}/{repo_owner}_{repo_name}_evaluation_output.json'
    path = f'../data/output_evaluation_data_jamba/{model_dir}/{repo_owner}_{repo_name}_evaluation_output_2.json'
    # path = f'../data/output_evaluation_data_lama_mod/{model_dir}/{repo_owner}_{repo_name}_evaluation_output_mod.json'
    # path = f'../data/output_evaluation_data_jamba_mod/{model_dir}/{repo_owner}_{repo_name}_evaluation_output_2_mod.json'
    with open(path, 'w') as file: # create new JSON file for GitHub repository
        json.dump(tmp_json, file) # write tmp_json to new file


def write_postprocessed_repo(repo_owner, repo_name, model_type):
    '''
    Function which writes processed GitHub repository to a documentation file.

    Args:
        repo_owner: The name of the GitHub repository owner.
        repo_name: The name of the GitHub repository.
        model_type: Name of used LLM.

    Return:
        None
    '''
    # check value of model_type to specify the path
    if model_type == 'llama3.1-8b': 
        # path = '../data/helper/helper_readme_eval_processed_m1_lama.json'
        path = '../data/helper/helper_readme_eval_processed_m1_jamba.json'
        # path = '../data/helper/helper_readme_eval_processed_m1_lama_mod.json'
        # path = '../data/helper/helper_readme_eval_processed_m1_jamba_mod.json'
    elif model_type == 'reka-flash': 
        # path = '../data/helper/helper_readme_eval_processed_m2_lama.json'
        path = '../data/helper/helper_readme_eval_processed_m2_jamba.json'
        # path = '../data/helper/helper_readme_eval_processed_m2_lama_mod.json'
        # path = '../data/helper/helper_readme_eval_processed_m2_jamba_mod.json'
    elif model_type == 'jamba-1.5-mini':
        # path = '../data/helper/helper_readme_eval_processed_m3_lama.json'
        path = '../data/helper/helper_readme_eval_processed_m3_jamba.json'
        # path = '../data/helper/helper_readme_eval_processed_m3_lama_mod.json'
        # path = '../data/helper/helper_readme_eval_processed_m3_jamba_mod.json'

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

model_type = 'jamba-1.5-mini'
# 'reka-flash' 0.45 credit / 1 millionen token --> 2.2 million tokens per day (model2)
# 'llama3.1-8b' 0.19 credit / 1 million token --> 5.26 million tokens per day (model1)
# 'jamba-1.5-mini' 0.10 credit / 1 million token --> 10 million tokens per day (model3)

# specify llm parameters for summary creation
model1_params = {
   'temperature': 0, # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex --> Internetrecherche hat keine anderen Empfehlungen ergeben
   # 'top_p': # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex
    'max_tokens': 1000
}

model2_params = {
   'temperature': 0, # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex --> Internetrecherche hat keine anderen Empfehlungen ergeben
   # 'top_p': # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex
    'max_tokens': 1000
}

model3_params = {
   'temperature': 0, # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex --> Internetrecherche hat keine anderen Empfehlungen ergeben
   # 'top_p': # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex
    'max_tokens': 1000
}

print('Model parameters are defined.')
print('---------------------------------------------')

loaded_data = open_json(path='../data/df_repos_counts_filtered.json') # load json with filtered repository
df = pd.DataFrame(loaded_data) # create Pandas dataframe with loaded_data
print('Dataframe is created.')
print('---------------------------------------------')
# create repo_list from df, each row of the df is represented as tuple (repo_owner, repo_name) 
repo_list = [(row.repo_owner, row.repo_name) for row in df.itertuples()]

num_of_all_tokens = 0 # number of processed tokens # new day --> 0
cnt = 0 # for testing
flag_break_loops = False # flag to break all loops

for i in repo_list: # iterate through all entries in repo_list --> each tuple represent a GitHub repository
    if cnt >= 51: # for testing
        break
    # >= 5200000 --> llama3.1-8b
    # >= 2200000 --> reka-flash
    # >= 9000000 --> jamba-1.5-mini
    if num_of_all_tokens >= 5200000: 
            print('Number of tokens for daily processing reached. Continue at the next day.')
            print('---------------------------------------------')
            break # if num_of_all_tokens >= 5200000 the loop should bread to prevent computing errors from Snowflake
    
    if not check_readme_eval_processed(repo_owner=i[0], repo_name=i[1], model_type=model_type): # call check_readme_eval_processed() for i (specific repository)
        print(f'README for "{i[1]}" will be processed.')
        repo_name = i[1] # set repo_name to i[1]
        repo_owner = i[0] # set repo_owner to i[0]    

        # evaluation for generated readme
        # path = f'../data/output_readme_data_lama/{repo_owner}_{repo_name}_output.json'
        path = f'../data/output_readme_data_jamba/{repo_owner}_{repo_name}_output_2.json'
        # path = f'../data/output_readme_data_lama_mod/{repo_owner}_{repo_name}_output_mod.json'
        # path = f'../data/output_readme_data_jamba_mod/{repo_owner}_{repo_name}_output_2_mod.json'
        readme_generated_data = open_json(path=path) # call open_json()
        readme_generated = readme_generated_data['readme'] # set variable for generated readme

        prompt_evaluation_generated = write_evaluation_prompt(repo_name=repo_name, input_txt=readme_generated) # call write_evaluation_prompt()
        evaluation_generated, evaluation_generated_tokens, evaluation_generated_total_tokens = send_query(prompt_evaluation=prompt_evaluation_generated, model_type=model_type) # call send_query() to create evaluation for readme
        score_generated_dir = [] #clean_score(evaluation_generated, model_type) # call clean_score() 
        print(f'Evaluation for generated README successfully created.')

        # evaluation for original readme
        readme_original_data = open_json(path=f'../data/input_readme_data/{repo_owner}_{repo_name}.json') # call open_json()
        readme_original = readme_original_data['readme'] # set variable for original readme 

        prompt_evaluation_original = write_evaluation_prompt(repo_name=repo_name, input_txt=readme_original) # call write_evaluation_prompt()
        evaluation_original, evaluation_original_tokens, evaluation_original_total_tokens = send_query(prompt_evaluation=prompt_evaluation_original, model_type=model_type) # call send_query() to create evaluation for readme
        score_original_dir = [] #clean_score(evaluation_original, model_type) # call clean_score()
        print(f'Evaluation for original README successfully created.')

        # save evaluation and call write_json()
        write_json(
            model_type=model_type, 
            repo_owner=repo_owner, 
            repo_name=repo_name, 
            readme_original=readme_original, 
            evaluation_original=evaluation_original, 
            evaluation_original_tokens=evaluation_original_tokens,
            evaluation_original_score=score_original_dir,
            readme_generated=readme_generated,
            evaluation_generated=evaluation_generated,
            evaluation_generated_tokens=evaluation_generated_tokens,
            evaluation_generated_score=score_generated_dir
        )

        write_postprocessed_repo(repo_owner=repo_owner, repo_name=repo_name, model_type=model_type) # call write_postprocessed_repo()
        print(f'Evaluations for repository "{repo_name}" from "{repo_owner}" successfully created.')

        num_of_all_tokens += evaluation_generated_total_tokens # increase num_of_all_tokens by evaluation_generated_total_tokens
        num_of_all_tokens += evaluation_original_total_tokens # increase num_of_all_tokens by evaluation_original_total_tokens

        print('---------------------------------------------')
        print(f'Number of processed tokens: {num_of_all_tokens}')
        cnt += 1 # for testing


        print('---------------------------------------------')
    else: # if current repository is already processed continue with the next one
        continue


snowflake_session.close() # close snowflake session
print('---------------------------------------------')
print('Snowflake session is closed.')
