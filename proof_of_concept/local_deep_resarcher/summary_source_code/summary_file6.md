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
input_file_name = 'configuration.py'
input_file = '
import os
from dataclasses import dataclass, fields
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from dataclasses import dataclass

from enum import Enum

class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"
    DUCKDUCKGO = "duckduckgo"

@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the research assistant."""
    max_web_research_loops: int = int(os.environ.get("MAX_WEB_RESEARCH_LOOPS", "3"))
    local_llm: str = os.environ.get("OLLAMA_MODEL", "llama3.2")
    search_api: SearchAPI = SearchAPI(os.environ.get("SEARCH_API", SearchAPI.DUCKDUCKGO.value))  # Default to DUCKDUCKGO
    fetch_full_page: bool = os.environ.get("FETCH_FULL_PAGE", "False").lower() in ("true", "1", "t")
    ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/")

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})

'
    
ChatGPT:

{
    "project_name": "ollama-deep-researcher",
    "file_name": "configuration.py",
    "tags": ["configuration", "environment-variables", "research-assistant"],
    "sum": "Defines configuration parameters using environment variables and dataclass.",
    "code": [
        "class SearchAPI(Enum):",
        "@dataclass(kw_only=True) class Configuration:",
        "@classmethod def from_runnable_config(cls, config: Optional[RunnableConfig] = None) -> \"Configuration\":"
    ]
}


