import os, re
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from celery import Celery
from sqlalchemy import select
from common.models import Image
from common.db import get_db

BROKER_URL = os.getenv("CELERY_BROKER")
celery = Celery("gateway", broker=BROKER_URL)

app = FastAPI(title="Image Import Service")

class ImportRequest(BaseModel):
    folder_url: HttpUrl

@app.post("/import/google-drive", status_code=202)
async def import_drive(req: ImportRequest):
    match = re.search(r"/folders/([a-zA-Z0-9_-]+)", req.folder_url)
    if not match:
        raise HTTPException(400, "Invalid Drive folder URL")
    folder_id = match.group(1)
    task_id = celery.send_task("tasks.import_google_drive", args=[folder_id]).id
    return {"task_id": task_id}

@app.get("/images")
async def list_images(db=Depends(get_db)):
    result = await db.execute(select(Image))
    return result.scalars().all()
