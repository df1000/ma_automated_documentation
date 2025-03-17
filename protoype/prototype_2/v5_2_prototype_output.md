copilot (erstellt am 2025-03-17)

## Ollama Deep Researcher

**Ollama Deep Researcher** is a lightweight web research and summarization assistant. It utilizes LangGraph, LangChain, and Ollama to conduct research, generate search queries, gather relevant information, and create concise summaries.

## Installation

### Prerequisites
- Python >= 3.9
- Docker (optional, for containerized deployment)

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/[your-repo]/ollama-deep-researcher.git
   cd ollama-deep-researcher
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
   Alternatively, using `pyproject.toml`:
   ```sh
   pip install .
   ```
3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Set API keys and configurations inside `.env`

4. (Optional) Run with Docker:
   ```sh
   docker build -t ollama-deep-researcher .
   docker run --env-file .env -p 8080:8080 ollama-deep-researcher
   ```

## Usage

1. Define research queries and parameters in `configuration.py`.
2. Run the research assistant:
   ```sh
   python -m ollama_deep_researcher
   ```
3. The assistant will:
   - Generate search queries
   - Fetch information using Tavily, DuckDuckGo, and other sources
   - Summarize the gathered research
4. Modify `prompts.py` to customize search query generation and summarization instructions.

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new feature branch:
   ```sh
   git checkout -b feature-name
   ```
3. Make and commit your changes:
   ```sh
   git commit -m "Add new feature"
   ```
4. Push the branch and create a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

For further assistance, open an issue on GitHub or refer to the documentation in the repository.

