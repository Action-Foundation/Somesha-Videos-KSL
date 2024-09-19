from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cv2
import numpy as np
import requests
import tempfile
import os
from typing import List
import logging
import urllib3
import vimeo  

# Suppress only the single InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoURLs(BaseModel):
    urls: List[str]

MAX_VIDEOS = 1010

# Vimeo API credentials
VIMEO_ACCESS_TOKEN = "35b24d71f540bfa24e61d488cf34e457"  # Replace with your Vimeo token
VIMEO_UPLOAD_URL = "https://api.vimeo.com/me/videos"


def download_video(url):
    try:
        response = requests.get(url, verify=False, timeout=30)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    except requests.RequestException as e:
        logger.error(f"Failed to download video from {url}: {str(e)}")
        raise Exception(f"Failed to download video from {url}: {str(e)}")

def combine_videos(urls):
    if not urls:
        return None

    if len(urls) > MAX_VIDEOS:
        raise HTTPException(status_code=400, detail=f"Maximum of {MAX_VIDEOS} videos allowed")

    temp_files = []
    for url in urls:
        if url.strip():
            # Check if it's a newline character

            try:
                temp_files.append(download_video(url.strip()))
            except Exception as e:
                logger.error(f"Error downloading video: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))

    if not temp_files:
        raise HTTPException(status_code=400, detail="No valid videos to combine")

    try:
        # Trim video to 400 milliseconds for newline characters
        
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
    except Exception as e:
        logger.error(f"Error combining videos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error combining videos: {str(e)}")

def upload_to_vimeo(video_path):
    try:
        # Step 1: Request an upload link (initialize the upload)
        headers = {
            'Authorization': f'Bearer {VIMEO_ACCESS_TOKEN}',
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.vimeo.*+json;version=3.4'
        }

        # Video metadata and upload initialization
        upload_data = {
            'upload': {
                'approach': 'tus',  # Use the 'tus' approach for large file uploads
                'size': os.path.getsize(video_path)
            },
            'name': 'Uploaded Video',
            'description': 'This video was uploaded using the Vimeo Upload API.'
        }

        # Send request to create an upload ticket
        response = requests.post(VIMEO_UPLOAD_URL, json=upload_data, headers=headers)
        response.raise_for_status()
        vimeo_data = response.json()

        # Extract the upload link
        upload_link = vimeo_data['upload']['upload_link']
        video_uri = vimeo_data['uri']  # Used to get the video link after upload

        # Step 2: Upload the video file using the provided upload link
        tus_headers = {
            'Tus-Resumable': '1.0.0',
            'Upload-Offset': '0',
            'Content-Type': 'application/offset+octet-stream',
            'Authorization': f'Bearer {VIMEO_ACCESS_TOKEN}'
        }

        with open(video_path, 'rb') as video_file:
            tus_response = requests.patch(upload_link, headers=tus_headers, data=video_file)
            tus_response.raise_for_status()

        # Step 3: Confirm the upload and retrieve the Vimeo video link
        video_response = requests.get(f"https://api.vimeo.com{video_uri}?fields=link", headers=headers)
        video_response.raise_for_status()
        video_link = video_response.json()['link']

        print(f"Video uploaded successfully: {video_link}")
        return video_link

    except requests.RequestException as e:
        print(f"Error uploading video to Vimeo: {str(e)}")
        raise

@app.post("/combine_videos")
async def process_urls(video_urls: VideoURLs):
    try:
        combined_video_path = combine_videos(video_urls.urls)
        if combined_video_path:
            vimeo_url = upload_to_vimeo(combined_video_path)
            os.remove(combined_video_path)  # Clean up the local file
            return {"vimeo_url": vimeo_url}
        else:
            raise HTTPException(status_code=400, detail="Failed to combine videos")
    except HTTPException as he:
        logger.error(f"HTTP Exception: {str(he)}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)