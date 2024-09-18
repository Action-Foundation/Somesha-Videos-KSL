import gradio as gr
import requests

BACKEND_URL = "http://localhost:8080/combine_videos"

def add_url(url_list, new_url):
    if new_url.strip():
        url_list.append(new_url.strip())
    return "\n".join(url_list), ""

def clear_urls(url_list):
    return "", []

def combine_videos(url_list, video_history):
    urls = [url for url in url_list.split("\n") if url.strip()]
    if not urls:
        return "Error: No URLs provided", gr.update(visible=False), "", video_history
    
    try:
        response = requests.post(BACKEND_URL, json={"urls": urls}, timeout=300)  # 5-minute timeout
        response.raise_for_status()
        vimeo_url = response.json()["vimeo_url"]
        video_id = vimeo_url.split("/")[-1]
        embed_html = f'<div style="padding:56.25% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/{video_id}?badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write" style="position:absolute;top:0;left:0;width:100%;height:100%;" title="Combined Video"></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>'
        
        # Add the new video to the history
        video_history.append({"url": vimeo_url, "embed": embed_html})
        
        return f"Video combined and uploaded successfully. Vimeo URL: {vimeo_url}", gr.update(value=embed_html, visible=True), vimeo_url, video_history
    except requests.RequestException as e:
        error_message = f"Error: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            error_message += f"\nServer response: {e.response.text}"
        return error_message, gr.update(visible=False), "", video_history

def display_video(video_history, index):
    if 0 <= index < len(video_history):
        return video_history[index]["embed"], video_history[index]["url"]
    return "", ""

def download_video(vimeo_url):
    if vimeo_url:
        return vimeo_url
    return None

with gr.Blocks() as demo:
    gr.Markdown("# Video Combiner")
    
    with gr.Row():
        url_input = gr.Textbox(label="Enter a video URL")
        add_button = gr.Button("Add URL")
        clear_button = gr.Button("Clear URLs")
    
    url_list = gr.Textbox(label="Added URLs", lines=5)
    combine_button = gr.Button("Combine Videos")
    
    output_text = gr.Textbox(label="Output")
    video_output = gr.HTML(label="Combined Video")
    vimeo_url_output = gr.Textbox(label="Vimeo URL", interactive=False)
    
    video_history = gr.State([])
    video_index = gr.Number(value=0, label="Video Index", interactive=True)
    
    display_button = gr.Button("Display Video")
    download_button = gr.Button("Download Video")

    url_list_state = gr.State([])

    add_button.click(add_url, inputs=[url_list_state, url_input], outputs=[url_list, url_input])
    clear_button.click(clear_urls, inputs=[url_list_state], outputs=[url_list, url_list_state])
    combine_button.click(combine_videos, inputs=[url_list, video_history], outputs=[output_text, video_output, vimeo_url_output, video_history])
    display_button.click(display_video, inputs=[video_history, video_index], outputs=[video_output, vimeo_url_output])
    download_button.click(download_video, inputs=[vimeo_url_output], outputs=[gr.File()])

if __name__ == "__main__":
    demo.launch(share=True)