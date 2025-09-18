# automated_documentation  

## Description  
This repository contains the source code for the thesis *Intelligent Documentation: Automated Generation of GitHub README Files with Large Language Models and Dynamic Prompts*. 
All written and used Python scripts and Juypter Notebooks are available in this repository. The provided source code does not create an application or programm to generate a README for a specified repository.  
It shows the applied approach to answer the corresponding research question:    
+ How does the quality of README files generated with an Large Language Model and custom prompts compare to the original README for a GitHub repository?
+ Does the quality of the original README vary when GitHub repositories are chosen based on specific criteria?

## Usage
This repository has five directories:  
+ proof_of_concept 
+ github_api
+ pre_processing
+ model
+ evaluate_results
The structure of this repository is viusualized in paragraph **Structure**.   

## Structure
```bash
automated_documentation/
├── LICENSE.md
├── README.md
├── evaluate_results
│   ├── 01_evaluate_df_llama.ipynb
│   ├── 02_evaluate_df_jamba.ipynb
│   ├── 03_1_evaluate_df_llama_mod.ipynb
│   ├── 03_2_evaluate_df_jamba_mod.ipynb
│   ├── 03_3_evalution_question_score_first_and_modified_prompt.ipynb
│   ├── 03_4_evalution_total_score_first_and_modified_prompt.ipynb
│   ├── helper_clean_score_m1.ipynb
│   ├── helper_clean_score_m2.ipynb
│   └── helper_clean_score_m3.ipynb
├── github_api
│   ├── 00_get_repo_metadata.py
│   ├── 01_get_repo_metadata.py
│   ├── 02_get_repo_data.py
│   ├── helper_get_poc_repos.ipynb
│   ├── helper_rezip_files.py
│   └── helper_zip_files.py
├── model
│   ├── 01_summary_readme.py
│   ├── 01_summary_readme_mod.py
│   ├── 02_readme_evaluation.py
│   ├── helper_count_files.py
│   ├── helper_count_tokens.ipynb
│   ├── helper_read_readme.ipynb
│   ├── helper_readme_length.ipynb
│   ├── readmes_manual_checked
│   │   ├── JakeWharton_pidcat.ipynb
│   │   ├── andkret_cookbook.ipynb
│   │   ├── awslabs_aws-config-to-elasticserach.ipynb
│   │   ├── lennylxx_ipv6-hosts.ipynb
│   │   ├── majumderb_rezero.ipynb
│   │   ├── realpython_cookiecutter-flask-skeleton.ipynb
│   │   └── sebastianruder_NLP-progress.ipynb
│   └── test_readme
│       ├── openstack_generated.md
│       └── openstack_original.md
├── preprocessing
│   ├── 01_repos_metadata.ipynb
│   ├── 02_analyse_repos_metadata.ipynb
│   ├── 03_get_split_of_repos.ipynb
│   ├── 04_data_cleaning.py
│   ├── 05_counts.ipynb
│   ├── helper_clean_filenames.ipynb
│   ├── helper_plot_first_request_metadata.ipynb
│   └── test
│       └── test_read_readme.ipynb
├── proof_of_concept
│   └── local_deep_resarcher
│       ├── poc1_output.md
│       ├── poc2_output.md
│       ├── poc_input.json
│       ├── readme_original.md
│       └── summary_source_code
│           ├── summary_file1.md
│           ├── summary_file10.md
│           ├── summary_file11.md
│           ├── summary_file2.md
│           ├── summary_file3.md
│           ├── summary_file4.md
│           ├── summary_file5.md
│           ├── summary_file6.md
│           ├── summary_file7.md
│           ├── summary_file8.md
│           └── summary_file9.md
├── ignore_repo.txt
└── requirements.txt
```


