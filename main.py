from fastapi import FastAPI

app = FastAPI()

@app.get("/welcome")
def welcome():
    return {
        "message": "Welcome to the FastAPI application on port 5000!"
        }