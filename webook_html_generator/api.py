import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles

from webook_html_generator.config import Config
from webook_html_generator.generator import Generator


def load_config() -> Config:
    dotenv_path = ".env"
    load_dotenv(dotenv_path=dotenv_path, override=True)
    return Config()


config: Config = load_config()
os.makedirs(config.upload_dir, exist_ok=True)


def run_rsync_to_bucket():
    """Run rsync to sync the upload_dir with the google cloud bucket"""
    os.system(
        f"gsutil -m rsync -r {config.upload_dir} gs://{config.google_cloud_bucket}"
    )


def sync_from_bucket():
    """Sync the upload_dir with the google cloud bucket"""
    os.system(f"gsutil -m rsync -r gs://{config.google_cloud_bucket} {config.upload_dir}")


app = FastAPI(title="htmlgenerator")
app.mount(
    "/screendisplay", StaticFiles(directory=config.upload_dir), name="screendisplay"
)

sync_from_bucket()

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000)


@app.get("/ping")
async def root():
    return {"message": "Pong"}


@app.get("/generate")
async def generate():
    generator = Generator(config)
    generator.handler()

    if config.google_cloud_sync and config.google_cloud_bucket:
        run_rsync_to_bucket()

    return {"message": "Generated successfully"}
