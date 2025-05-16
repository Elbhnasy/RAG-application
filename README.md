# mini-rag

This is a minimal implementation of the RAG model for question answering.

## Requirements

- Python 3.12 

#### Install Python using MiniConda

1) Download and install MiniConda from [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)
2) Create a new environment using the following command:
```bash
$ conda create -n RAG
```
3) Activate the environment:
```bash
$ conda activate RAG
```

## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt
```

### Setup the environment variables

```bash
$ cp .env.example .env
```

Set your environment variables in the `.env` file. Like `OPENAI_API_KEY` value.

### Run Fastapi server (development mode)
```bash
$ fastapi dev main.py
```
## Docker Setup

### Development Environment

You can run this application using Docker for a containerized development environment. The following commands help manage Docker containers, images, and volumes.

```bash
# Stop all running containers
$ docker stop $(docker ps -aq)

# Remove all containers
$ docker rm $(docker ps -aq)

# Remove all images
$ docker rmi $(docker images -q)

# Remove all volumes
$ docker volume rm $(docker volume ls -q)

# Clean up unused Docker resources
$ docker system prune -a

# Start the application with Docker Compose
$ docker compose up -d
```

The `docker-compose.yml` file sets up all required services for this application, including the RAG service and any dependent services. The `-d` flag runs containers in detached mode.

### Production Deployment

For production deployment, additional configuration may be required. Please refer to the Docker documentation for more information on production deployments.

### POSTMAN Collection
You can use the provided Postman collection to test the API endpoints. Import the [mini-rag.postman_collection.json](assets/Mini-Rag.postman_collection.json) file into Postman and run the requests.