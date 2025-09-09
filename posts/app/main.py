from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI(title="Posts")

class PostIn(BaseModel):
    body: str
    media: list[str] = []
    visibility: str = "public"

@app.post("/posts")
def create_post(payload: PostIn, current_user=None):
    post_id = str(uuid.uuid4())
    # persist to DB (omitted here)
    # produce PostCreated event to Redpanda/Kafka (omitted)
    return {"id": post_id, "body": payload.body, "media": payload.media}
