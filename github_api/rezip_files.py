import zipfile
import os

# Path to the original ZIP file
original_zip = "../data/repo_data_zip/lonePatient_awesome-pretrained-chinese-nlp-models_2025-04-21_11-03-06.zip"


# Directory to extract the contents
extracted_dir = "../data/repo_data_unzip/"

# Extract all files
with zipfile.ZipFile(original_zip, 'r') as zip_ref:
    zip_ref.extractall(extracted_dir)


# lisa-linux@LAPTOP-VLI78DI6:~/stuff/ma_automated_documentation/github_api$ python3 rezip_files.py