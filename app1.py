import gradio as gr
import cv2
import numpy as np
import requests
import tempfile
import os

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

    temp_files = [download_video(url) for url in urls.split('\n') if url.strip()]
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

def process_urls(urls):
    combined_video = combine_videos(urls)
    if combined_video:
        return combined_video
    else:
        return "Failed to combine videos. Please check your URLs."

# Create Gradio interface
iface = gr.Interface(
    fn=process_urls,
    inputs=gr.Textbox(lines=5, placeholder="Enter video URLs, one per line"),
    outputs=gr.Video(),
    title="KSL Video Combiner",
    description="Enter KSL video URLs (one per line) to combine them into a single video.",
)

# Launch the interface
iface.launch(share=True)