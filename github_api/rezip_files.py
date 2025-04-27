import zipfile
import os

# Path to the original ZIP file
original_zip = "../data/raw_repo_data/abi_screenshot-to-code_2025-04-21_09-10-25.zip"


# Directory to extract the contents
extracted_dir = "../data/repo_unzip/"

# Extract all files
with zipfile.ZipFile(original_zip, 'r') as zip_ref:
    zip_ref.extractall(extracted_dir)


# lisa-linux@LAPTOP-VLI78DI6:~/stuff/ma_automated_documentation/github_api$ python3 rezip_files.py