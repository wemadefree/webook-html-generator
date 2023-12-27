import os
from datetime import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles

from webook_html_generator.config import Config
from webook_html_generator.generator import Generator


def run_rsync_to_bucket():
    """Run rsync to sync the upload_dir with the google cloud bucket"""
    os.system(f"gsutil rsync -r {Config.upload_dir} gs://{Config.google_cloud_bucket}")


def sync_from_bucket():
    """Sync the upload_dir with the google cloud bucket"""
    os.system(f"gsutil rsync -r gs://{Config.google_cloud_bucket} {Config.upload_dir}")


app = FastAPI(title="htmlgenerator")
app.mount(
    "/screendisplay", StaticFiles(directory=Config.upload_dir), name="screendisplay"
)

sync_from_bucket()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


@app.get("/ping")
async def root():
    return {"message": "Pong"}


@app.get("/generate")
async def generate():
    generator = Generator()
    generator.handler()

    if Config.google_cloud_sync and Config.google_cloud_bucket:
        run_rsync_to_bucket()

    return {"message": "Generated successfully"}
