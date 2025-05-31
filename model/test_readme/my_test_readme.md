## dl-docker
================

### Repository Summary

The `dl-docker` repository provides a pre-configured Docker container for running Jupyter Notebooks with TensorFlow, allowing users to easily set up and use a deep learning environment without manual installation and configuration.

### Installation

To get started, follow these steps:

1. Install Docker on your machine if you haven't already.
2. Clone the repository using `git clone https://github.com/floydhub/dl-docker.git`.
3. Navigate to the repository directory and run `docker build -t dl-docker .` to build the Docker image.
4. Run `docker run -p 8888:8888 dl-docker` to start the Docker container.
5. Open a web browser and navigate to `http://localhost:8888` to access the Jupyter Notebook server.

### Usage

The Jupyter Notebook server is pre-configured with TensorFlow and password protection. To access the server, use the password specified in the `PASSWORD` environment variable. You can switch between different kernel options, including Python 2, using the `c.MultiKernelManager` class.

### Contributing

Contributions are welcome! If you'd like to contribute to the project, please fork the repository and submit a pull request. Make sure to follow the standard guidelines for contributing to open-source projects.

### License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

### Overall Architecture

The repository uses a simple and straightforward architecture, with the Dockerfile defining the environment and dependencies, and the Jupyter Notebook server running within the container. The password protection mechanism is implemented using environment variables, ensuring secure access to the Jupyter Notebook server. The multi-kernel support is achieved through the use of the `c.MultiKernelManager` class.