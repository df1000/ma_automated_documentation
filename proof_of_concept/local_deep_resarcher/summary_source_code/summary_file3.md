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
input_file_name = 'langgraph.json'
input_file = '
    {
        "dockerfile_lines": [],
        "graphs": {
          "ollama_deep_researcher": "./src/assistant/graph.py:graph"
        },
        "python_version": "3.11",
        "env": "./.env",
        "dependencies": [
          "."
        ]
      }
    '
    
ChatGPT:

{
  "project_name": "ollama-deep-researcher",
  "file_name": "langgraph.json",
  "tags": ["configuration", "dependency-management", "graph-processing"],
  "sum": "Defines project dependencies, environment, and graph processing entry point.",
  "code": [
    "\"graphs\": { \"ollama_deep_researcher\": \"./src/assistant/graph.py:graph\" }",
    "\"python_version\": \"3.11\"",
    "\"env\": \"./.env\""
  ]
}
