import zipfile
import os

# Path to the original ZIP file
original_zip = "../data/raw_data_zip/raw_data_range_0_22196.zip"

# Directory to extract the contents
extracted_dir = "../data/raw_data/"

# Extract all files
with zipfile.ZipFile(original_zip, 'r') as zip_ref:
    zip_ref.extractall(extracted_dir)


# lisa-linux@LAPTOP-VLI78DI6:~/stuff/ma_automated_documentation/github_api$ python3 zip_files.py