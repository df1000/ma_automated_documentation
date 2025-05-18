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
input_file_name = 'state.py'
input_file = '
import operator
from dataclasses import dataclass, field
from typing_extensions import TypedDict, Annotated

@dataclass(kw_only=True)
class SummaryState:
    research_topic: str = field(default=None) # Report topic     
    search_query: str = field(default=None) # Search query
    web_research_results: Annotated[list, operator.add] = field(default_factory=list) 
    sources_gathered: Annotated[list, operator.add] = field(default_factory=list) 
    research_loop_count: int = field(default=0) # Research loop count
    running_summary: str = field(default=None) # Final report

@dataclass(kw_only=True)
class SummaryStateInput:
    research_topic: str = field(default=None) # Report topic     

@dataclass(kw_only=True)
class SummaryStateOutput:
    running_summary: str = field(default=None) # Final report
'
    
ChatGPT:

{
    "project_name": "ollama-deep-researcher",
    "file_name": "state.py",
    "tags": ["dataclasses", "state-management", "typing"],
    "sum": "Defines states and input-output structure for managing research process.",
    "code": [
        "class SummaryState:\n    research_topic: str = field(default=None)\n    search_query: str = field(default=None)\n    web_research_results: Annotated[list, operator.add] = field(default_factory=list)",
        "class SummaryStateInput:\n    research_topic: str = field(default=None)",
        "class SummaryStateOutput:\n    running_summary: str = field(default=None)"
    ]
}


