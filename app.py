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

MAX_VIDEOS = 10

'''
# Vimeo client setup
client = vimeo.VimeoClient(
    token='6c0e53613726874a46da7c0f286e27b5',
    key='45dc18a3c7bdb1dc6255a49d784398b14b4fd55f',
    secret='jVwFHFHWs0pGs0rdlHzCnDvkJFru1IeNACt0ygV9bk3mMU45hzZGvg/I+vTzzzvpU1HakvxdxITzf/gokrq5k8VPwQmGirosmltJZAf9/CIAnPpKw19lGrr13MKXKQ1m'
)
'''

# Vimeo client setup
client = vimeo.VimeoClient(
    token='35b24d71f540bfa24e61d488cf34e457',
    key='9efa7b1c1827ce4b1d74330d0a90cf62ff4da8b9',
    secret='QIwoszSklYElk2wH5PHqe/EzSDB8HM+gdHBg4iaiDs2SkYa+RS3T4ei/VrPWGMMZt2qGXYIbjxfNlPYOtz5g3Ylsys0VpBuiUjkRhz+oR6yR2epl/MW68V1ZxS/D7EwD'
)

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
            try:
                temp_files.append(download_video(url.strip()))
            except Exception as e:
                logger.error(f"Error downloading video: {str(e)}")
                raise HTTPException(status_code=400, detail=str(e))

    if not temp_files:
        raise HTTPException(status_code=400, detail="No valid videos to combine")

    try:
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
        # Upload the video to Vimeo
        uri = client.upload(video_path, data={
            'name': 'Combined Video',
            'description': 'This video was combined using our app.'
        })
        
        # Get the Vimeo URL
        response = client.get(uri + '?fields=link').json()
        vimeo_url = response['link']
        
        return vimeo_url
    except vimeo.exceptions.VideoUploadFailure as e:
        logger.error(f"Video upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload to Vimeo: {str(e)}")
    except vimeo.exceptions.APIRateLimitExceededFailure:
        logger.error("API rate limit exceeded")
        raise HTTPException(status_code=429, detail="API rate limit exceeded. Please try again later.")
    except Exception as e:
        logger.error(f"Unexpected error during Vimeo upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload to Vimeo: {str(e)}")

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