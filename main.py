from fastapi import FastAPI

# Initialize the FastAPI application instance
app = FastAPI()

# Define a root GET endpoint
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# Define a dynamic GET endpoint with a path parameter
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query_param": q}
