import os

#directory = '../data/output_readme_data'
directory = '../data/input_readme_data'
file_count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])

print(f'Number of files: {file_count}')

# python3 helper_count_files.py