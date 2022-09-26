"""Main script file - FastAPI app"""

import json
from dataclasses import dataclass, field

from fastapi import FastAPI, Response, HTTPException, Request

app = FastAPI()




@app.get("/")
def read_root():
    return Response("The API is working")


@app.post("/post-test")
async def post_test(data: Request) -> Response:
    """Test POST request"""
    post_data = await data.json()
    return Response(content=json.dumps(post_data), media_type="application/json")


