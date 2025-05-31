import os
from dotenv import load_dotenv
from snowflake.snowpark.session import Session
from snowflake.cortex import Complete
from transformers import AutoTokenizer
from huggingface_hub import login
import pandas as pd
import json


def open_json(path):
    try:
        with open(path, 'r') as file:
            loaded_data = json.load(file)
        return loaded_data
    except json.decoder.JSONDecodeError:
        return {}


def check_repo_processed(repo_owner, repo_name):
    try:
        repo_to_check = [repo_owner, repo_name]
        with open('../data/helper/repos_processed.json', 'r') as file:
            data_list = json.load(file)
    except json.JSONDecodeError:
        data_list = []

    if repo_to_check in data_list:
        print(f'Repo "{repo_name}" from "{repo_owner} is already processed.')
        return True
    else: 
        return False


def write_summary_prompt(repo_name, input_txt):
    prompt_summary = f'''
        You are acting like software development expert for the following GitHub repository "{repo_name}".
        Your task is to summarize the given source code string "{input_txt}" in natural language so a specialist is able to understand
        the purpose of the repository.
        Identify its purpose, key functionalites, main components and dependencies. Focus on the overall architecture and structure 
        rather than line-by-line details. Do not add any recomandations or improvement suggestions but concentrate on the summary. 
        Present the summary in a clear and concise language. 
    ''' 
    prompt_summary = prompt_summary.replace("'", "\\'") # to prevent error in sql statement

    return prompt_summary


def write_readme_prompt(repo_name, repo_owner, summary_txt, license, requirements):
    # markdown format passt noch nicht. sieht scheiße aus --> mit print() sieht das Format gut aus
    # with open('../test_readme/my_test_readme.md', 'w') as file:
    # file.write(readme)
    # varible so speichern und dann sieht das format gut aus ;-)
    prompt_readme = f'''
        You are acting like software development expert for the following GitHub repository "{repo_name}" from the owner "{repo_owner}". 
        Your task is to create a README for the repository in Markdown format. 
        Use the provided summary: "{summary_txt}", the license: "{license}" and the given requirements: "{requirements}".
        If license and requirements are "None", try to find the missing content in the provided summary.
        The README file should contain information about what the project does, why it is useful, how users 
        can get started, where they can get help, and how to maintain and contribute to the project.
        If you don't know the answer add a hint following this style […]. 
        You're not allowed to create made-up content to fill gaps and or add additional paragraphs.

        Use the following Markdown template and fill each paragraph. 

        ## Titel

        ## Installation

        ## Usage

        ## Contributing

        ## License

        Do not include any sensitive data like names or emails. Keep the output clean, structured and well formated using Markdown. 
        Your are not allowed to add any small talk.
    '''
    prompt_readme = prompt_readme.replace("'", "\\'")  # to prevent error in sql statement

    return prompt_readme


def count_tokens(num_of_chars):
    num_of_tokens = num_of_chars / 3.99

    return num_of_tokens


def send_query(prompt, type):
    if type == 'summary':
        model_params = model_summary_params
    elif type == 'readme':
        model_params = model_readme_params

    try:
        query = f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                '{model}',
                [
                    {{
                        'role': 'user', 
                        'content': '{prompt}'
                    }}
                ],
                {{
                    'temperature': {model_params['temperature']},
                    'max_tokens':  {model_params['max_tokens']}
                }} 
            ) AS response
        """
        response = snowflake_session.sql(query).collect()
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
    max_tokens = 200 #127000
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

    with open(f'../data/output_data/{repo_owner}_{repo_name}_output.json', 'w') as file:
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
    "warehouse": 'COMPUTE_WH'
}

# build Snowflake session with connection parameters
snowflake_session = Session.builder.configs(connection_params).create()
('Snowflake sessions is build.')
print('---------------------------------------------')

# # define llm for summary
# # characters_per_token: 3.99 -->  3.9 mio characters per day
# # number of input tokens: 128,000
# # number of output tokens: 8,192
model = 'llama3.1-8b'
model_summary_params = {
   'temperature': 0, # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex --> Internetrecherche hat keine anderen Empfehlungen ergeben
   # 'top_p': # default: 0 https://docs.snowflake.com/en/sql-reference/functions/complete-snowflake-cortex
    'max_tokens': 5000
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

num_of_all_tokens = 0
cnt = 0

for i in repo_list:
    if cnt >= 1:
        break
    if num_of_all_tokens >= 5000000: # 1 credit / 0.19 million tokens per credit --> 5.26 million tokens per day
            print('Number of tokens for daily processing reached. Continue at the next day.')
            print('---------------------------------------------')
            break

    if not check_repo_processed(repo_owner=i[0], repo_name=i[1]): 
        print(f'Repository "{i[1]}" will be processed.')
        repo_name = i[1]
        repo_owner = i[0]
        num_of_chars = i[2]
        repo_data = open_json(path=f'../data/input_data/{repo_owner}_{repo_name}.json')
        source_code_cleaned_comments = repo_data['source_code_cleaned_comments']
        license = repo_data['license']
        requirements = repo_data['requirements']

        prompt_summary = write_summary_prompt(repo_name=repo_name, input_txt=source_code_cleaned_comments)
        print(f'Summary prompt for "{repo_name}" is created.')
        
        num_of_tokens = count_tokens(num_of_chars=num_of_chars)
        #num_of_all_tokens =+ num_of_tokens
        
        summary_list = []

        if num_of_tokens < 1100: #127000:
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
            cnt += 1
            

        else:
            print(f'Number of tokens of repository: "{repo_name}" to big to preprocess in single query. Subprompts are requiered.')
            sub_prompts = create_subprompts(source_code_cleaned_comments) # list with chunks #.replace("'", "\\'"))

            sub_prompt_num = 1
        
            for prompt in sub_prompts:
                sub_prompt = prompt.replace('<|begin_of_text|>\n', '')

                prompt_summary = write_summary_prompt(repo_name=repo_name, input_txt=sub_prompt)
                sub_summary, sub_summary_tokens = send_query(prompt_summary, type='summary')
                
                tmp_json = {
                    f'summary_{sub_prompt_num}': sub_summary,
                }

                sub_prompt_num += 1
                summary_list.append(tmp_json)
                num_of_all_tokens =+ sub_summary_tokens

            print(f'summary_list: {summary_list}')
            tmp_list = [list(d.values())[0] for d in summary_list] 
            print(f'tmp_list: {tmp_list}')
            summary = ''.join(tmp_list)

            prompt_readme = write_readme_prompt(repo_name=repo_name, repo_owner=repo_owner, summary_txt=summary, license=license, requirements=requirements)
            readme, readme_tokens, readme_completion_tokens, readme_prompt_tokens = send_query(prompt=prompt_readme, type='readme')

            write_json(repo_owner=repo_owner, repo_name=repo_name, summary_list=summary_list, readme=readme, readme_total_tokens=readme_tokens, readme_completion_tokens=readme_completion_tokens, readme_prompt_tokens=readme_prompt_tokens)
            write_preprocessed_repo(repo_owner=repo_owner, repo_name=repo_name)

            print(f'Summary and README for repository: "{repo_name}" from "{repo_owner}" successfully created.')

            num_of_all_tokens += readme_tokens
            print('---------------------------------------------')
            print(f'Number of processed tokens: {num_of_all_tokens}')
            cnt += 1 

        print('---------------------------------------------')
    else:
        continue
    
snowflake_session.close()
print('Snowflake session is closed.')
