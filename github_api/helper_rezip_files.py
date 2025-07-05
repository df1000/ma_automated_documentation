#
# Hint: If lines are created with support of a Large Language Model or the code is taken from another source, you find following hint at the end of the line:
#       (generated with Microsoft Copilot) or (source: link_to_source)

import zipfile
import os

# Path to the original ZIP file
original_zip = "../data/repo_data_zip/jd_tenacity_2025-06-07_13-20-35.zip"


# Directory to extract the contents
extracted_dir = "../data/repo_data_unzip/"

# Extract all files
with zipfile.ZipFile(original_zip, 'r') as zip_ref:
    zip_ref.extractall(extracted_dir)


# lisa-linux@LAPTOP-VLI78DI6:~/stuff/ma_automated_documentation/github_api$ python3 helper_rezip_files.py