import pandas as pd
import json
import numpy as np
import os
from functools import reduce
import re
import shutil
from pathlib import Path
import zipfile


def unzip_files(path_to_zip):
    # Path to the original ZIP file
    original_zip = path_to_zip
    # Directory to extract the contents
    extracted_dir = '../data/repo_data_unzip/'
    # Extract all files
    with zipfile.ZipFile(original_zip, 'r') as zip_ref:
        zip_ref.extractall(extracted_dir)
    
    extracted_contents = os.listdir(extracted_dir)
    extracted_folder_path = os.path.join(extracted_dir, extracted_contents[0]) if extracted_contents else None

    return extracted_folder_path


def read_md(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
    return md_content


def remove_comments(text):
    single_line_comments_pattern = r'#.*' # (generated with Microsoft Copilot)
    mulit_line_comments_pattern = r"\"\"\".*?\"\"\"|'''.*?'''" # (generated with Microsoft Copilot)
    cleaned_str = re.sub(single_line_comments_pattern, '', text)
    cleaned_str = re.sub(mulit_line_comments_pattern, '', cleaned_str, flags=re.DOTALL) # (generated with Microsoft Copilot)

    return cleaned_str


def remove_space_newline(text):
    cleaned_str = text.replace(' ', '').replace('\n', '')

    return cleaned_str


def remove_urls(text):
  
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+' # (source: https://github.com/souradipp76/ReadMeReady --> scripts/data.ipynb)
    cleaned_str = re.sub(url_pattern, '', text)
  
    return cleaned_str


def remove_html(text):
    html_pattern = r'<.*?>' # (source: https://github.com/souradipp76/ReadMeReady --> scripts/data.ipynb)
    cleaned_str = re.sub(html_pattern, '', text)
  
    return cleaned_str


def remove_emoji(text): # (source: https://github.com/souradipp76/ReadMeReady --> scripts/data.ipynb)
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols 
                           u"\U0001F680-\U0001F6FF"  # transport 
                           u"\U0001F1E0-\U0001F1FF"  # flags 
                           u"\U00002702-\U000027B0" 
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    
    cleaned_str = emoji_pattern.sub(r'', text)

    return cleaned_str


def clean_code(text):
    clean1 = remove_space_newline(text)
    clean2 = remove_urls(clean1)
    clean3 = remove_html(clean2)
    cleaned_str = remove_emoji(clean3)

    return cleaned_str


input_data_path = '../data/input_readme_data'

df = pd.DataFrame(columns=['repo_owner', 'repo_name', 'source_code_comments', 'source_code', 'source_code_cleaned_comments', 'source_code_cleaned'])

root_dir = Path('../data/repo_data_zip')
#cnt = 0 # for testing
for zip_file in root_dir.iterdir():
    # for testing
    # if cnt >=1:
    #     break
    #if zip_file.suffix == '.zip':

    print(f'Next subdirectory {zip_file.name} will be processed.')
    path_to_zip = f'{root_dir}/{zip_file.name}'
    print(f'path_to_zip: {path_to_zip}')
    repo_path_unzip = unzip_files(path_to_zip)
    #print(f'repo_path_unzip: {repo_path_unzip}')
    
    # repo_parts = repo_path_unzip.split('/')[-1].split('-')
    # repo_name = '-'.join(reduce(lambda x, y: x + '-' + y, repo_parts[:-1]).split('-')[1:])
    # repo_owner = repo_path_unzip.split('/')[3].split('-')[0]

    repo_parts = path_to_zip.split('.')[-2].split('/')[-1]
    #repo_parts = path_to_zip.split('/')[-1]
    print(f'repo_parts: {repo_parts}')

    pattern = r"^(.*?)(_?\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})$" # (generated with Microsoft Copilot)
    match = re.match(pattern, repo_parts)

    if match:
        result = match.group(1)
    else:
        print('no result')

    pattern2 = r'-'

    if re.search(pattern2, result):
        repo_owner = result.split('_')[0]
        repo_name = result.split('_')[1]
    else:

        repo_owner = result.split('_')[0]
        repo_name = result.split('_')[1:]
        repo_name = '_'.join(repo_name)


    tmp_json = {
        'repo_owner': repo_owner,
        'repo_name': repo_name,
        'requirements': None,
        'readme': None,
        'license': None,
        'source_code_comments': None,
        'source_code': None,
        'source_code_cleaned_comments': None,
        'source_code_cleaned': None
    }

    check_readme = False
    check_license = False
    check_requirements = False
    list_source_code = []

    exclude_dirs = ('dist', 'env', 'venv', 'vendor', 'third_party', 'tmp', 'temp', 'logs', 'assets', 'static', 'build', 'tests', 'docs', 'doc', 'documentation', 'dep', 'dependencies') 

    for root, dirs, files in os.walk(repo_path_unzip): # root: current directory path | dirs: list of subdirectories in the current path | files: list of files in the current directory
        # filters directories which are listed in exclude_dirs from dirs
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')] # dirs[:]: update the list (list from os.walk()) dirs instead of creating a new one (generated with Microsoft Copilot)

        for file in files: # iterate through all files in files list
            try:
                file_path = os.path.join(root, file)
                if file.lower() in ('readme.md', 'readme.txt', 'readme') and check_readme is False:
                    tmp_json['readme'] = read_md(file_path)
                    check_readme = True
                elif file.lower() in ('license.md', 'license.txt', 'license') and check_license is False:
                    tmp_json['license'] = read_md(file_path)
                    check_license = True
                elif file == 'requirements.txt' and check_requirements is False:
                    with open(file_path) as data:
                        requirements_content = data.readlines()
                        tmp_json['requirements'] = ''.join(line.strip() for line in requirements_content)
                        check_requirements = True
                elif file.endswith(('.py', '.ipynb')):
                    with open(file_path, 'r', errors='ignore') as f:
                        # list_source_code.append((file_path, f.read())) # to check if all files are in list_source_code add file_path
                        list_source_code.append(f.read())
                    # print(f'from {file_path} the file: {file} was added to list_source_code')
            except Exception as e:
                print(f'Error during processing file {file_path}: {e}')

    source_code_comments = ''.join(line.strip() for line in list_source_code)
    tmp_json['source_code_comments'] = source_code_comments

    source_code_no_comments = remove_comments(source_code_comments)
    tmp_json['source_code'] = source_code_no_comments

    tmp_json['source_code_cleaned'] = clean_code(source_code_no_comments)
    tmp_json['source_code_cleaned_comments'] = clean_code(source_code_comments)

    new_row = {
    'repo_owner': tmp_json['repo_owner'],
    'repo_name': tmp_json['repo_name'],
    'source_code_comments': len(tmp_json['source_code_comments']),
    'source_code': len(tmp_json['source_code']),
    'source_code_cleaned_comments': len(tmp_json['source_code_cleaned_comments']),
    'source_code_cleaned': len(tmp_json['source_code_cleaned'])
    }

    df = df._append(new_row, ignore_index=True)

    with open(f'{input_data_path}/{repo_owner}_{repo_name}.json', 'w') as file:
        json.dump(tmp_json, file)
        print(f'.json for {repo_owner}_{repo_name} is saved')

    # delete unzip file for saving memory
    shutil.rmtree(repo_path_unzip)
    print(f'unzipped file for repo {repo_owner}_{repo_name} is deleted')

    #cnt += 1

tmp_json = df.to_json(orient='records', lines=False, force_ascii=False)
with open('../data/df_repos_counts.json', 'w') as file:
    file.write(tmp_json)