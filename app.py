from flask import Flask, render_template, request, jsonify
from flask_ngrok import run_with_ngrok
import os
import base64
import subprocess
import logging
import asyncio
import shlex
import ffmpeg

app = Flask(__name__)
# run_with_ngrok(app)

logging.basicConfig(filename='flask_log.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

def execute_model_infer():
    try:
        command = [
            "python", 
            "infer.py",
            "config_filename='configs/LRS3_V_WER32.3.ini'",
            "data_filename='uploaded_video/processed_video.mp4'",
            "detector=mediapipe"
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, cwd = "Visual_Speech_Recognition_for_Multiple_Languages")
        print(result)

        return {"result": result.stdout, "error": None}
    
    except Exception as e:
        return {"result": None, "error": e}

async def process_video():
    command = shlex.split("ffmpeg -i 'uploaded_video/video.mp4' -ss 3 -t 11 -c copy uploaded_video/processed_video.mp4")
    print("debug", command)
    
    await subprocess.run(command, capture_output=True, text=True, cwd = "Visual_Speech_Recognition_for_Multiple_Languages")


@app.route('/')
def index():
    app.logger.info('Info level log')
    app.logger.warning('Warning level log')
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' in request.files:
        video_file = request.files['video']
        
        # Save the uploaded video file to a folder (change as needed)
        upload_folder = 'Visual_Speech_Recognition_for_Multiple_Languages/uploaded_video'
        os.makedirs(upload_folder, exist_ok=True)
        video_path = os.path.join(upload_folder, 'video.mp4')
        video_file.save(video_path)

        # asyncio.run(process_video())
        start_time = '00:00:00' # Start time for trimming (HH:MM:SS)
        end_time = '00:00:10' # End time for trimming (HH:MM:SS)

        (
            ffmpeg.input("Visual_Speech_Recognition_for_Multiple_Languages/uploaded_video/video.mp4", ss=start_time, to=end_time)
            .output("Visual_Speech_Recognition_for_Multiple_Languages/uploaded_video/processed_video.mp4")
            .run(overwrite_output=True)
        )
        
        # Read the video file and encode it in base64
        video_data = base64.b64encode(video_file.read()).decode('utf-8')
        
        # video -> subtitle_content
        result = execute_model_infer()

        # Sample WebVTT content
        subtitle_content = "WEBVTT\n\n00:00.000 --> 00:10.000\n model: PROFOUND HEARING LOSSES ARE BOTH THINGS SO I UNDERSTAND THE DIFFICULTIES THAT THOSE OF US WITH HEARING LOSS AND FAITH\n real: I HAVE A PROFOUND HEARING LOSS IN BOTH EARS SO I UNDERSTAND THE DIFFICULTIES THAT THOSE OF US WITH A HEARING LOSS CAN FACE"

        # Encode WebVTT content to base64
        subtitle_data = base64.b64encode(subtitle_content.encode('utf-8')).decode('utf-8')

        # Respond with the base64-encoded video data
        return jsonify({'video_data': video_data, "subtitle_data": subtitle_data, "processed_video": result})
    else:
        return jsonify({'error': 'No video file provided'}), 400

if __name__ == '__main__':
    app.run(debug=True)
