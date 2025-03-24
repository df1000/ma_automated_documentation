import requests
import base64
import json
import getpass

# Replace with your GitHub personal access token
ACCESS_TOKEN = getpass.getpass()

# GitHub API base URL
BASE_URL = "https://api.github.com"

# Example repository (owner/repo)
owner = "Taniiishk"
repo = "Rock-Paper-Scissors-Game"

import requests
import base64
import json

ACCESS_TOKEN = "your_github_access_token"
BASE_URL = "https://api.github.com"
owner = "octocat"
repo = "Hello-World"

headers = {"Authorization": f"token {ACCESS_TOKEN}"}

def get_repo_content(owner, repo, path=""):
    url = f"{BASE_URL}/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch content: {response.status_code}")
        return None

def fetch_all_files(owner, repo, path=""):
    contents = get_repo_content(owner, repo, path)
    if not contents:
        return []

    files = []
    for item in contents:
        if item["type"] == "file":
            try:
                content_response = requests.get(item["download_url"])
                content_response.raise_for_status()  # Raise HTTP errors if any
                content = base64.b64decode(content_response.content).decode("utf-8")
                file_data = {
                    "name": item["name"],
                    "path": item["path"],
                    "content": content,
                }
                files.append(file_data)
            except UnicodeDecodeError:
                print(f"Skipping binary file: {item['name']}")
            except Exception as e:
                print(f"Error fetching file {item['name']}: {e}")
        elif item["type"] == "dir":
            files.extend(fetch_all_files(owner, repo, item["path"]))
    return files

repo_files = fetch_all_files(owner, repo)
with open("repo_content.json", "w", encoding="utf-8") as json_file:
    json.dump(repo_files, json_file, indent=4)

print("Repository content saved as repo_content.json")