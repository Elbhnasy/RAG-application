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