# Author: Lisa Wallner  
# Description: In this notebook a file with the relevant metadata of multiple GitHub repositories will be created.  
# Depencencies:  
# - data/raw_data_zip/raw_data_no_range.zip  
# - data/raw_data_zip/raw_data_0_22196.zip

import pandas as pd
import json
from pathlib import Path
from langdetect import detect
import zipfile
import os


def load_json(path):
    with open(path, 'r') as file:
        loaded_data = json.load(file)
    
    return loaded_data


def rezip_files(path, range_type):
    
    original_zip = path # path to the original ZIP file
    if range_type == 'range':
        extracted_dir = '../data/raw_data/range' # directory where the extract contents are saved
    else:
        extracted_dir = '../data/raw_data/no_range'

    with zipfile.ZipFile(original_zip, 'r') as zip_ref: 
        zip_ref.extractall(extracted_dir) # extract all files


# columns which are requiered for preprocessing and further steps
columns = [
    'id', 
    'name', 
    'full_name', 
    'html_url', 
    'description', 
    'url', 
    'labels_url', 
    'created_at', 
    'updated_at', 
    'pushed_at', 
    'size', 
    'stargazers_count', 
    'watchers_count', 
    'language', 
    'has_issues', 
    'has_projects', 
    'has_downloads', 
    'has_wiki', 
    'has_pages', 
    'has_discussions', 
    'forks_count', 
    'open_issues_count', 
    'license', 
    'allow_forking', 
    'topics', 
    'visibility', 
    'forks', 
    'open_issues', 
    'watchers', 
    'default_branch', 
    'score'
]

# file with repos up to 22196 stars
file_no_range = '../data/df_repos_metadata_up_to_max_test.json'
# file with repos 0 to 22196 stars
file_range = '../data/df_repos_metadata_0_to_22196_test.json'

help_columns = load_json(path='../data/helper/help_columns.json')
keys = list(help_columns[0].keys()) # get keys of loaded_data as list

# loaded zip files of metadata in raw_data
path_no_range = '../data/raw_data_zip/raw_data_no_range.zip'
path_range = '../data/raw_data_zip/raw_data_range_0_22196.zip'
rezip_files(path=path_no_range, range_type='no_range')
rezip_files(path=path_range, range_type='range')

directory_path = Path('../data/raw_data/range') 
all_files_range = [file.name for file in directory_path.iterdir() if file.is_file()]

# create empty df with keys of loaded_data as columns
df_raw_range = pd.DataFrame(columns=keys)

for file in all_files_range:
    data = load_json(path=f'../data/raw_data/range/{file}')
    #  iterate through subdictionary in data and concatenate the content of the subdictionary to df_repos
    for repo in data:
        # create tmp df_repo for each repo
        df_tmp = pd.DataFrame(data=[repo], columns=keys)
        # concatenate df_repos with df_repo
        df_raw_range = pd.concat([df_raw_range, df_tmp], ignore_index=True)

for k in keys:
    if k in columns:
        continue
    else:
        df_raw_range = df_raw_range.drop([k], axis=1)