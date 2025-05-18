## Created with ChatGPT 2025-03-17 

User:
You are acting like GitHub documentation expert for a project called {project_name}. Your task is to create an output in JSON format which should have the following structure:

{
    'project_name': '',
    'file_name': '',
    'tags': [],
    'sum': '',
    'code': []
} 

You have to create the values for each key. Search for suitable tags (maximum of 3) for {input_file}. The value for 'sum' should contain concise summary. Don't use detailed sentences. If {input_file} contains code elements, include the most ciritcal parts (maximum of 3), focus on functionality and leaving out excessive details in the list for the key 'code', otherwise leave the value empty. It is not allowed to copy the entire code into the list, focus on the most significant parts that describe the purpose of the file. Remove '/n' and do not escape any characters.

Write your output in JSON format and keep it clean and structured. Use the given parameters and do not include any sensitive data like names or emails.

project_name = 'ollama-deep-researcher'
input_file_name '.env.example'
input_file = 'OLLAMA_BASE_URL=                # the endpoint of the Ollama service, defaults to http://localhost:11434 if not set
OLLAMA_MODEL=                   # the name of the model to use, defaults to 'llama3.2' if not set

# Which search service to use, either 'duckduckgo' or 'tavily' or 'perplexity'
SEARCH_API=
# Web Search API Keys (choose one or both)
TAVILY_API_KEY=tvly-xxxxx      # Get your key at https://tavily.com
PERPLEXITY_API_KEY=pplx-xxxxx  # Get your key at https://www.perplexity.ai

MAX_WEB_RESEARCH_LOOPS=
FETCH_FULL_PAGE=
    '
    
ChatGPT:

{
    "project_name": "ollama-deep-researcher",
    "file_name": ".env.example",
    "tags": ["configuration", "environment", "API"],
    "sum": "Example environment configuration file for setting up API keys and model parameters.",
    "code": [
        "OLLAMA_BASE_URL= # Defaults to http://localhost:11434 if not set",
        "SEARCH_API= # Defines the web search service to use",
        "TAVILY_API_KEY=tvly-xxxxx # API key for Tavily search service"
    ]
}