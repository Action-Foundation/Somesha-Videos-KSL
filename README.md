```markdown
# Video Combiner Tool

## Overview

The Video Combiner Tool is a web application that allows users to combine multiple videos from provided URLs into a single video file. The combined video is then uploaded to Vimeo, and a playable link is generated for easy sharing. This tool is built using FastAPI for the backend and Gradio for the user interface.

## Features

- Combine multiple videos from URLs into one video.
- Upload the combined video to Vimeo.
- Generate a shareable link to the combined video.
- User-friendly interface for adding video URLs.

## Technologies Used

- **Backend**: FastAPI
- **Frontend**: Gradio
- **Video Processing**: OpenCV
- **Video Upload**: PyVimeo (Vimeo API)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or later
- Access to a Vimeo account with API access
- Installed required Python packages

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/video-combiner.git
   cd video-combiner
   ```

2. **Create a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install required packages**:
   ```bash
   pip install fastapi[all] opencv-python PyVimeo gradio requests
   ```

4. **Set up Vimeo API credentials**:
   - Create a `.env` file in the root directory of your project and add your Vimeo API credentials:
     ```
     VIMEO_ACCESS_TOKEN=your_access_token
     VIMEO_CLIENT_ID=your_client_id
     VIMEO_CLIENT_SECRET=your_client_secret
     ```

## Running the Application

1. **Start the FastAPI server**:
   Navigate to the directory containing `app.py` and run:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8080
   ```

2. **Launch the Gradio interface**:
   In another terminal, navigate to the directory containing `main.py` and run:
   ```bash
   python main.py
   ```

3. **Access the application**:
   Open your web browser and go to `http://localhost:7860` to access the Gradio interface.

## Usage Instructions

1. **Add Video URLs**:
   - Enter a valid video URL in the input box and click "Add URL".
   - Repeat this step to add multiple video URLs.

2. **Combine Videos**:
   - Once you have added all desired video URLs, click on "Combine Videos".
   - The application will process your request, combine the videos, and upload them to Vimeo.

3. **View Combined Video**:
   - After processing, an embedded Vimeo player will display your combined video.
   - The direct link to your Vimeo video will also be shown below the player for easy sharing.

4. **Download Option** (if implemented):
   - You can download the combined video directly if this feature is enabled.

## Troubleshooting

- Ensure that all provided URLs are valid and accessible.
- Check your Vimeo account settings if you encounter issues with uploading videos.
- Make sure all required packages are installed correctly.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please create an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/)
- [Gradio](https://gradio.app/)
- [OpenCV](https://opencv.org/)
- [Vimeo API](https://developer.vimeo.com/)
```

### Notes:

1. Replace `https://github.com/yourusername/video-combiner.git` with your actual GitHub repository URL.
2. Ensure that you create a LICENSE file if you mention licensing in your README.
3. Adjust any sections as necessary based on additional features or changes in your project structure.

This README provides clear instructions on how to set up, run, and use your Video Combiner Tool, making it easier for users to understand its functionality and get started quickly!