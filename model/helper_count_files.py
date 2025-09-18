# This file provides code to the number of files in a specific directory
# Hint: If lines are created with support of a Large Language Model or the code is taken from another source, you find following hint at the end of the line:
#       (generated with Microsoft Copilot) or (source: link_to_source)

import os

directory = '../data/output_evaluation_data_lama_mod/model2'
#directory = '../data/output_evaluation_data_/model3'
file_count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])

print(f'Number of files: {file_count}')

# commad for execution in cli
# python3 helper_count_files.py