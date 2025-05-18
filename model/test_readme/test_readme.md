 ## Popular GitHub Repositories by Programming Language

This repository is a Python script that fetches and generates a list of most popular repositories on GitHub based on the given programming language. It uses the GitHub API to retrieve the required information and stores the access token in a local file named "token.json". The script supports multiple programming languages and can fetch up to 10 pages of results per language.

## Installation

To use this script, you need to have Python installed on your system. You can install the required dependencies using pip:

```bash
pip install requests argparse json humanize
```

## Usage

To run the script, save the provided code in a file named `github_popular_repos.py` and execute it using the following command:

```bash
python github_popular_repos.py [--language LANG1, LANG2, ...]
```

Replace `LANG1, LANG2, ...` with the desired programming languages, separated by commas. If no languages are specified, the script will fetch the popular repositories for all supported languages.

The script generates a markdown file named `repos.md` in the same directory with the most popular repositories for the given languages.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

[MIT License](LICENSE)

## Development

To run the script in development mode, you can use the following command:

```bash
python -m unittest tests.test_github_popular_repos.py
```

This will run the unit tests for the script. The tests cover the main functionality of the script and ensure that the expected results are generated.

## Dependencies

The script depends on the following Python libraries:

- `requests`: for making HTTP requests
- `argparse`: for parsing command-line arguments
- `json`: for parsing JSON responses
- `time`: for handling time-related functionality
- `humanize`: for formatting dates
- `datetime`: for parsing and manipulating dates

You can install these dependencies using pip:

```bash
pip install requests argparse json humanize
```