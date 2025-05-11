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
input_file_name = 'docker-image.yml'
input_file = '
name: Docker Image CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

env:
  # Use docker.io for Docker Hub if empty
  REGISTRY: ghcr.io
  # github.repository as <account>/<repo>
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      # Setup QEMU for multi-platform build support
      # https://docs.docker.com/build/ci/github-actions/multi-platform/
      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3 

      # Set up BuildKit Docker container builder to be able to build
      # multi-platform images and export cache
      # https://github.com/docker/setup-buildx-action
      - name: Setup Docker buildx
        uses: docker/setup-buildx-action@v3

      # Login against a Docker registry except on PR
      # https://github.com/docker/login-action
      - name: Log into registry ${{ env.REGISTRY }}
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GH_TOKEN }}

      # Extract metadata (tags, labels) for Docker
      # https://github.com/docker/metadata-action
      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}

      # Build and push Docker image with Buildx (don't push on PR)
      # https://github.com/docker/build-push-action
      - name: Build and push Docker image
        id: build-and-push
        uses: docker/build-push-action@v5
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
          labels: ${{ steps.meta.outputs.labels }}
'
    
ChatGPT:

{
    "project_name": "ollama-deep-researcher",
    "file_name": "docker-image.yml",
    "tags": ["CI/CD", "Docker", "GitHub Actions"],
    "sum": "Defines CI workflow for Docker image build and push.",
    "code": [
        "steps:\n      - name: Checkout repository\n        uses: actions/checkout@v4",
        "steps:\n      - name: Setup Docker buildx\n        uses: docker/setup-buildx-action@v3",
        "steps:\n      - name: Build and push Docker image\n        id: build-and-push\n        uses: docker/build-push-action@v5\n        with:\n          platforms: linux/amd64,linux/arm64\n          push: true\n          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest"
    ]
}


