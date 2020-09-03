from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.main import app

client = TestClient(app)


# def test_docs():
#     """Return HTML docs for root route."""
#     response = client.get('/')
#     assert response.status_code == 200
#     assert response.headers['content-type'].startswith('text/html')

@app.get("/")
async def read_main():
    return {"msg": "Hello World"}

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}