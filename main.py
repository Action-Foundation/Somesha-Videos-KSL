# Interface

import gradio as gr
import requests
import os

# FastAPI backend URL
BACKEND_URL = "http://localhost:8000/combine_videos"

def add_url(url_list, new_url):
    if new_url.strip():
        url_list.append(new_url.strip())
    return "\n".join(url_list), ""

def combine_videos(url_list):
    urls = url_list.split("\n")
    response = requests.post(BACKEND_URL, json={"urls": urls})
    
    if response.status_code == 200:
        video_path = response.json()["video_path"]
        return video_path
    else:
        return f"Error: {response.text}"

with gr.Blocks() as demo:
    gr.Markdown("# KSL Video Combiner")
    
    with gr.Row():
        url_input = gr.Textbox(label="Enter a video URL")
        add_button = gr.Button("Add URL")
    
    url_list = gr.Textbox(label="Added URLs", lines=5)
    combine_button = gr.Button("Combine Videos")
    
    video_output = gr.Video(label="Combined Video")
    download_button = gr.Button("Download Video")

    url_list_state = gr.State([])

    add_button.click(add_url, inputs=[url_list_state, url_input], outputs=[url_list, url_input])
    combine_button.click(combine_videos, inputs=[url_list], outputs=[video_output])
    
    def enable_download_button(video_path):
        return gr.Button.update(interactive=True if video_path else False)
    
    video_output.change(enable_download_button, inputs=[video_output], outputs=[download_button])
    
    def download_video(video_path):
        return video_path
    
    download_button.click(download_video, inputs=[video_output], outputs=[gr.File()])

if __name__ == "__main__":
    demo.launch(share=True)