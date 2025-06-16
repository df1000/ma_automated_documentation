# Author: Lisa Wallner
# Description: In this Python script the content of the previous loaded GitHub repositories are cleaned and prepared for the next step - the summary and README creation.
# Depedencies:
#   - data/repo_data_zip/
#   - data/helper/helper_repos_metadata.json
#
# Hint: If lines are created with support of a Large Language Model or the code is taken from another source, you find following hint at the end of the line:
#       (generated with Microsoft Copilot) or (source: link_to_source)

import pandas as pd # package for data manipulation
import json # package to work with .json
import numpy as np # package for numeric operations
import os # package for using operating system
import re # package for regex patterns
import shutil # package to work with files and directories
from pathlib import Path # package to work with paths
import zipfile # package to work with ZIP files


def unzip_files(path_to_zip):
    '''
    Function which extract files from a zipped directory and save them into a new directory.

    Args:
        path_to_zip: Path to the ZIP file.

    Return:
        extracted_folder_path
    '''
    original_zip = path_to_zip # path to original ZIP directory
    extracted_dir = '../data/repo_data_unzip/' # directory where the extracted files should be saved

    with zipfile.ZipFile(original_zip, 'r') as zip_ref: # open ZIP in read mode # (generated with Microsoft Copilot)
        zip_ref.extractall(extracted_dir) # extract all files inside the ZIP and save them into extracted_dir # (generated with Microsoft Copilot)
    
    extracted_contents = os.listdir(extracted_dir) # list with filenames from extracted_dir
    # check if extracted_contents is not empty --> join extracted_dir with extracted_contents as path
        # eg. 
        # extracted_dir = '../data/repo_data_unzip/'
        # extracted_contents[0] = 'facebook-chisel-fdbf067'
        # --> extracted_folder_path = '../data/repo_data_unzip/facebook-chisel-fdbf067'
        # hint: ZIP directory has the following structure: ZIP_project/project/files...
    # is empty --> None
    extracted_folder_path = os.path.join(extracted_dir, extracted_contents[0]) if extracted_contents else None

    return extracted_folder_path


def read_md(file_path):
    '''
    Function open file and use 'utf-8' encoding for reading. Content will saved in variable.

    Args:
        file_path: Path to file.

    Return:
        md_content
    '''
    with open(file_path, 'r', encoding='utf-8') as file: # open and encode file from given path
                md_content = file.read() # save file content in md_content
    return md_content


def remove_email(text):
    '''
    Function which removes email strings with Regex pattern.

    Args:
        text: String to clean.

    Return:
        cleanded_str
    '''    
    email_pattern = '[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+[a-zA-Z0-9-.]+' # pattern to identify standard email addresses # (generated with Microsoft Copilot)
    cleaned_str = re.sub(email_pattern, '', text) # apply sub() to remove email_pattern from text
  
    return cleaned_str


def remove_comments(text):
    '''
    Function which removes single-line and multi-line comments with Regex pattern.

    Args:
        text: String to clean.

    Return:
        cleanded_str
    '''   
    single_line_comments_pattern = r'#.*' # pattern to identify single-line comments # (generated with Microsoft Copilot)
    mulit_line_comments_pattern = r"\"\"\".*?\"\"\"|'''.*?'''" # pattern to identify multi-line comments # (generated with Microsoft Copilot)
    cleaned_str = re.sub(single_line_comments_pattern, '', text) # apply sub() to remove single_line_comments_pattern from text
    # apply sub() to remove single_line_comments_pattern from text
    # re.DOTALL ensures that the pattern matches across multiple lines --> new lines are not ignored https://docs.python.org/3/library/re.html
    cleaned_str = re.sub(mulit_line_comments_pattern, '', cleaned_str, flags=re.DOTALL)  # (generated with Microsoft Copilot)

    return cleaned_str


def remove_space_newline(text):
    '''
    Function which removes spaces and newline symbols.

    Args:
        text: String to clean.

    Return:
        cleanded_str
    '''     
    cleaned_str = text.replace(' ', '').replace('\n', '') # replace space and newlines with ''

    return cleaned_str


def remove_urls(text):
    '''
    Function which identify and removes urls in given text using Regex pattern.

    Args:
        text: String to clean.

    Return:
        cleanded_str
    '''   
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+' # pattern to identify urls # (source: https://github.com/souradipp76/ReadMeReady --> scripts/data.ipynb)
    cleaned_str = re.sub(url_pattern, '', text) # apply sub() to remove url_pattern from text
  
    return cleaned_str


def remove_html(text):
    '''
    Function which identify and removes html tags in given text using Regex pattern.

    Args:
        text: String to clean.

    Return:
        cleanded_str
    '''      
    html_pattern = r'<.*?>' # pattern to identify html tags # (source: https://github.com/souradipp76/ReadMeReady --> scripts/data.ipynb)
    cleaned_str = re.sub(html_pattern, '', text) # apply sub() to remove html_pattern from text
  
    return cleaned_str


def remove_emoji(text): # (source: https://github.com/souradipp76/ReadMeReady --> scripts/data.ipynb)
    '''
    Function which identify and removes emojis or similar symbols in given text using Regex pattern.

    Args:
        text: String to clean.

    Return:
        cleanded_str
    '''   
    # re.compile() creates pattern which matches unicode emoji characters
    # [] contains different unicode ranges: emojis, symbols, ...   
    # flag=re.UNICODE --> pattern handels unicode characters correctly https://docs.python.org/3/library/re.html#contents-of-module-re
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols 
                           u"\U0001F680-\U0001F6FF"  # transport 
                           u"\U0001F1E0-\U0001F1FF"  # flags 
                           u"\U00002702-\U000027B0"  # other symbols
                           u"\U000024C2-\U0001F251"  # other icons
                           "]+", flags=re.UNICODE) 
    
    cleaned_str = emoji_pattern.sub(r'', text) # apply sub() to remove emoji_pattern from text

    return cleaned_str


def clean_code(text):
    '''
    Function which applies all cleaning functions to given text.

    Args:
        text: String to clean.

    Return:
        cleanded_str
    '''  
    clean0 = remove_email(text) # call remove_email()
    clean1 = remove_urls(clean0) # call remove_urls()
    clean2 = remove_html(clean1) # call remove_html()
    clean3 = remove_space_newline(clean2) # call remove_space_newline()
    cleaned_str = remove_emoji(clean3) # call remove_emoji()

    return cleaned_str


def remove_notebook_output(filepath):
    '''
    Function which removes output cells of Jupter Notebooks and returns the cleaned content as string. 

    Args:
        filepath: Path for Jupyter Notebook file.

    Return:
        file_str_to_save
    '''  
    with open(filepath, 'r', errors='ignore') as f: # read jupyter notebook as json
        data = json.load(f) # save loaded content in in variable 'data'
    
    # interate over all cells in the cells list inside the dictionary data
    # each cell represent a code or a markdown cell
    # data.get() --> try to get the key 'cells' from data, # if 'cells' exists its value will returned, if not an empty list will returned to avoid errors
    for cell in data.get('cells', []):
        if 'outputs' in cell: # check if cell has key 'outputs' 
            cell['outputs'] = None # set value of 'outputs' to None

    file_str_to_save = json.dumps(data) # save modified data variable to string

    return file_str_to_save


def get_repo_metadata(repo_path):
    '''
    Function which uses the given repo_path to select the fitting values for repo_owner and repo_name from helper_repos_metadata.json.

    Args:
        repo_path: Path of ZIP directory.

    Return:
        repo_owner, repo_name
    '''      
    with open('../data/helper/helper_repos_metadata.json', 'r') as f: # open and read file
        loaded_metadata = json.load(f) # save content of f in variable loaded_metadat
    
    for dictionary in loaded_metadata: # interate through all dictionaries in loaded_metadata
        if dictionary['original_filename'] == repo_path: # if dictionary['original_filename'] matches repo_path two variables will be assigned
            repo_owner = dictionary['repo_owner'] # get repository owner
            repo_name = dictionary['repo_name'] # get repository name
    
    return repo_owner, repo_name


################################################ script for each ZIP file starts here ################################################

input_data_path = '../data/input_readme_data' # define path where prepared files for next step will be saved

df = pd.DataFrame(columns=['repo_owner', 'repo_name', 'source_code_comments', 'source_code', 'source_code_cleaned_comments', 'source_code_cleaned']) # create dataframe with given columns to save data for further processing

root_dir = Path('../data/repo_data_zip') # set root directory to ZIP directories
# cnt = 0 # for testing
for zip_file in root_dir.iterdir(): # iterate over all ZIPs in root_dir

    # if cnt >=1: # for testing
    #     break

    print(f'Next subdirectory {zip_file.name} will be processed.')
    path_to_zip = f'{root_dir}/{zip_file.name}' # create path to specific ZIP
    print(f'path_to_zip: {path_to_zip}')
    repo_path_unzip = unzip_files(path_to_zip) # call unzip_files()
    print(f'repo_path_unzip: {repo_path_unzip}')

    repo_owner, repo_name = get_repo_metadata(repo_path=zip_file.name) # call get_repo_metadata()

    # create dict with given structure for further processing
    # necessary content for README creation will be saved in this dict
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
    
    check_readme = False # create variable check_readme
    check_license = False # create variable check_license
    check_requirements = False # # create variable check_requirements
    list_source_code = [] # create empty list for source code of ZIP

    # specifiy list which contains directory names which should not be processed in the next steps
        ## dist --> distribution files for packaging and deploying software
        ## env / venv --> virtual environments
        ## vendor --> third-party libraries or dependencies
        ## tmp / temp --> temporary files generated during execution or testing
        ## logs --> stored log files
        ## assets --> often used for images, fonts, videos, ...
        ## dep / dependencies --> third-party libraries or dependencies
        ## debug / debugs --> debugging-related files such as logs or temporary outputs
        ## chache --> store temporay files which should help to speed up the processes 
    exclude_dirs = ('dist', 'env', 'venv', 'vendor', 'third_party', 'tmp', 'temp', 'logs', 'assets', 'dep', 'dependencies', 'debug', 'debugs', 'chache') 

    # root: current directory path
    # dirs: list of subdirectories in the current path
    # files: list of files in the current directory
    # iterate through all directories and subdirectories from repo_path_unzip --> eg. '../data/repo_data_unzip/repo_XY/'
    # topdown = True --> function first lists the current directory (root), then its subdirectories (dirs), and finally its files (files)
    # --> toplevel is processed first!!!
    for root, dirs, files in os.walk(repo_path_unzip, topdown=True): # https://docs.python.org/3.9/library/os.html?highlight=os%20walk
        # filters directories which are listed in exclude_dirs from dirs
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')] # dirs[:]: update the list (list from os.walk()) dirs instead of creating a new one (generated with Microsoft Copilot)

        for file in files: # iterate through all files in files list
            # check file for the conditions
            try: 
                file_path = os.path.join(root, file) # create file_path --> eg. '../data/repo_data_unzip/repo_XY/file_XY.py'
                if file.lower() in ('readme.md', 'readme.txt', 'readme', 'readme.rst') and check_readme is False: # lower filename, check if filename fits to given values ('readme.md', 'readme.txt', 'readme', 'readme.rst') and if variable check_readme is False
                    tmp_json['readme'] = read_md(file_path) # call read_md()
                    check_readme = True # set variable to True
                elif file.lower() in ('license.md', 'license.txt', 'license.rst', 'license') and check_license is False: # lower filename, check if filename fits to given values ('license.md', 'license.txt', 'license.rst', 'license') and if variable check_license is False
                    tmp_json['license'] = read_md(file_path) # call read_md()
                    check_license = True # set variable to True
                elif file == 'requirements.txt' and check_requirements is False: # check if filename == to requirements.txt and variable check_requirements is False
                    with open(file_path) as data: # open file as data
                        requirements_content = data.readlines() # reads every line of data and save its content in requirements_content
                        tmp_json['requirements'] = ''.join(line.strip() for line in requirements_content) # leading and trailing whitespace is removed for each line, then lines are joined together into a single string
                        check_requirements = True # set variable to True
                elif file.endswith(('.py', '.ipynb')): # check if file has specific ending --> identifing source_code files
                    if file.endswith(('.ipynb')): # jupyter notebook will be handeld extra, because the output of the cells has to be removed to prevent exploiding of input for README creation and copyright violations (images, logos, ...)
                        file_str_to_save = remove_notebook_output(file_path) # call remove_notebook_output()
                        list_source_code.append(file_str_to_save) # append file_str_to_save to list_source_code
                    else: # remaing file is a Python script, there is no output
                        with open(file_path, 'r', errors='ignore') as f: # open and read content
                            list_source_code.append(f.read()) # append file content to list_source_code
            except Exception as e: # raise Exception if an error occurs
                print(f'Error during processing file {file_path}: {e}')

    source_code_comments = ''.join(line.strip() for line in list_source_code) # create string from list_source_code without modifications
    tmp_json['source_code_comments'] = source_code_comments # save source_code_comment in tmp_json

    source_code_no_comments = remove_comments(source_code_comments) # call remove_comments() and save output in source_code_no_comments
    tmp_json['source_code'] = source_code_no_comments # save source_code_no_comments in tmp_json

    tmp_json['source_code_cleaned'] = clean_code(source_code_no_comments) # call clean_code() and save output in tmp_json
    tmp_json['source_code_cleaned_comments'] = clean_code(source_code_comments) # call clean_code() and save output in tmp_json

    # create new row with content of tmp_json for later saving in dataframe
    new_row = {
        'repo_owner': tmp_json['repo_owner'],
        'repo_name': tmp_json['repo_name'],
        'source_code_comments': len(tmp_json['source_code_comments']), # number of characters
        'source_code': len(tmp_json['source_code']), # number of characters
        'source_code_cleaned_comments': len(tmp_json['source_code_cleaned_comments']), # number of characters
        'source_code_cleaned': len(tmp_json['source_code_cleaned']) # number of characters
    }

    df = df._append(new_row, ignore_index=True) # append new_row to existing df

    with open(f'{input_data_path}/{repo_owner}_{repo_name}.json', 'w') as file: # save tmp_json in new JSON file
        json.dump(tmp_json, file)
        print(f'.json for {repo_owner}_{repo_name} is saved')

    shutil.rmtree(repo_path_unzip)  # delete unzip file for saving memory

    print(f'unzipped file for repo {repo_owner}_{repo_name} is deleted')
    print('--------------------------------------')

    # cnt += 1 # for testing

tmp_json = df.to_json(orient='records', lines=False, force_ascii=False) # create new tmp_json from df with processed repositories
with open('../data/df_repos_counts.json', 'w') as file: # save tmp_json in JSON file for further analysis
    file.write(tmp_json) # write content of tmp_json to file