import os
from dotenv import load_dotenv

load_dotenv(override=True)
print(os.environ['FOOBAR'])
print(os.environ['HELLO'])