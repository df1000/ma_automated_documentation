copilot --> mischt formate... folgender text ist zusammenkopiert (original in onenote) (erstellt am 2025-03-17)
## ollama-deep-researcher

A lightweight web research and summarization assistant that leverages advanced graph processing and AI-powered search tools to facilitate efficient and insightful research workflows.

## Installation

To get started, ensure you have Docker installed. Use the provided `Dockerfile` to set up a containerized environment for the project. For configuration, use the `.env.example` file as a reference to set up API keys and model parameters.

```bash
# Build and run the Docker container
docker build -t ollama-deep-researcher .
docker run -p 8080:8080 ollama-deep-researcher
```

For manual setup, ensure Python 3.11 is installed and dependencies are satisfied using the pyproject.toml file.

## Usage
The assistant processes web research tasks, including query generation, data gathering, summarization, and knowledge gap analysis. Use the configuration.py and state.py to define the parameters and manage research states. Access the functionality through defined CLI commands or API endpoints (details to be added).

[More details on CLI commands and API usage will be added here.]

## Contributing
Contributions are welcome! Follow these steps:

1. Fork the repository.

2. Clone your fork and create a new branch.

3. Make your changes and test locally.

4. Commit and push your changes to your fork.

5. Open a pull request for review.

7. Please ensure your contributions align with the project's code standards and are thoroughly documented.

## License

[License information goes here. Please specify the applicable license for this project.]