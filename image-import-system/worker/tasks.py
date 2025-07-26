import os, uuid, asyncio
from celery import Celery
from sqlalchemy import insert
from common.db import engine
from common.models import Image
from .google import iter_public_images
from .storage import upload

BROKER = os.getenv("CELERY_BROKER")
celery = Celery("tasks", broker=BROKER)

@celery.task(name="tasks.import_google_drive", bind=True, acks_late=True, max_retries=3)
def import_google_drive(self, folder_id: str):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_async_import(folder_id))

async def _async_import(folder_id: str):
    async with engine.begin() as conn:
        for img in iter_public_images(folder_id):
            s3_key = f"{folder_id}/{uuid.uuid4()}_{img['name']}"
            storage_path = upload(img["path"], s3_key)

            stmt = insert(Image).values(
                google_drive_id = img["id"],
                name            = img["name"],
                size            = img["size"],
                mime_type       = img["mime"],
                storage_path    = storage_path,
                source          = "google-drive"
            ).prefix_with("IGNORE")  # MySQL: skip duplicates
            await conn.execute(stmt)
