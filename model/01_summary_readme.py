import os
from dotenv import load_dotenv
from snowflake.snowpark.session import Session
from snowflake.snowpark.context import get_active_session
from snowflake.cortex import Complete
import pandas as pd
import json

# # load .env file
load_dotenv()

# set up connection parameters for Snowflake connection
connection_params = {
    "account": os.environ['SNOWFLAKE_ACCOUNT'],
    "user": os.environ['SNOWFLAKE_USER'],
    "password": os.environ['SNOWFLAKE_USER_PASSWORD'],
    "role": 'ACCOUNTADMIN',
    "warehouse": 'COMPUTE_WH'
}

# build Snowflake session with connection parameters
snowflake_session = Session.builder.configs(connection_params).create()

# define llm for summary
# characters_per_token: 3.99 -->  3.9 mio characters per day
# number of input tokens: 128,000
# number of output tokens: 8,192
model = 'llama3.1-8b'
model_params = {
    'temperature':,
    'top_p': 
    'max_tokens': 2500
}



