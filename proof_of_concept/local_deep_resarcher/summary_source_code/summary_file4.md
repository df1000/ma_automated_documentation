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
input_file_name = 'pyproject.toml'
input_file = '
  [project]
  name = "ollama-deep-researcher"
  version = "0.0.1"
  description = "Lightweight web research and summarization assistant."
  authors = [
      { name = "Lance Martin" }
  ]
  readme = "README.md"
  license = { text = "MIT" }
  requires-python = ">=3.9"
  dependencies = [
      "langgraph>=0.2.55",
      "langchain-community>=0.3.9",
      "tavily-python>=0.5.0",
      "langchain-ollama>=0.2.1",
      "duckduckgo-search>=7.3.0",
      "beautifulsoup4>=4.13.3",
  ]
  
  [project.optional-dependencies]
  dev = ["mypy>=1.11.1", "ruff>=0.6.1"]
  
  [build-system]
  requires = ["setuptools>=73.0.0", "wheel"]
  build-backend = "setuptools.build_meta"
  
  [tool.setuptools]
  packages = ["assistant"]
  
  [tool.setuptools.package-dir]
  "assistant" = "src/assistant"
  
  [tool.setuptools.package-data]
  "*" = ["py.typed"]
  
  [tool.ruff]
  lint.select = [
      "E",    # pycodestyle
      "F",    # pyflakes
      "I",    # isort
      "D",    # pydocstyle
      "D401", # First line should be in imperative mood
      "T201",
      "UP",
  ]
  lint.ignore = [
      "UP006",
      "UP007",
      "UP035",
      "D417",
      "E501",
  ]
  
  [tool.ruff.lint.per-file-ignores]
  "tests/*" = ["D", "UP"]
  
  [tool.ruff.lint.pydocstyle]
  convention = "google"
  '
  
ChatGPT:

{
    "project_name": "ollama-deep-researcher",
    "file_name": "pyproject.toml",
    "tags": ["Python", "Project Configuration", "Build System"],
    "sum": "Project configuration file defining metadata, dependencies, and build system settings.",
    "code": [
        "[project]\nname = \"ollama-deep-researcher\"\nversion = \"0.0.1\"\ndescription = \"Lightweight web research and summarization assistant.\"\nrequires-python = \">=3.9\"",
        "dependencies = [\n    \"langgraph>=0.2.55\",\n    \"langchain-community>=0.3.9\",\n    \"tavily-python>=0.5.0\",\n    \"langchain-ollama>=0.2.1\",\n    \"duckduckgo-search>=7.3.0\",\n    \"beautifulsoup4>=4.13.3\"\n]",
        "[build-system]\nrequires = [\"setuptools>=73.0.0\", \"wheel\"]\nbuild-backend = \"setuptools.build_meta\""
    ]
}

