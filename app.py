from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cv2
import numpy as np
import requests
import tempfile
import os

app = FastAPI()

class VideoURLs(BaseModel):
    urls: list[str]

def download_video(url):
    response = requests.get(url)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    else:
        raise Exception(f"Failed to download video from {url}")

def combine_videos(urls):
    if not urls:
        return None

    temp_files = [download_video(url) for url in urls if url.strip()]
    captures = [cv2.VideoCapture(file) for file in temp_files]

    fps = captures[0].get(cv2.CAP_PROP_FPS)
    frame_size = (int(captures[0].get(cv2.CAP_PROP_FRAME_WIDTH)),
                  int(captures[0].get(cv2.CAP_PROP_FRAME_HEIGHT)))

    output_path = 'combined_video.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

    for cap in captures:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)

    for cap in captures:
        cap.release()
    out.release()

    for file in temp_files:
        os.remove(file)

    return output_path

@app.post("/combine_videos")
async def process_urls(video_urls: VideoURLs):
    try:
        combined_video = combine_videos(video_urls.urls)
        if combined_video:
            return {"video_path": combined_video}
        else:
            raise HTTPException(status_code=400, detail="Failed to combine videos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)