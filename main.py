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
run_with_ngrok(app)

logging.basicConfig(filename='flask_log.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

def execute_model_infer(filename):
    try:
        print("debug 1")
        command = [
            "python", 
            "infer.py",
            "config_filename='configs/LRS3_V_WER32.3.ini'",
            f"data_filename='uploaded_video/{filename}.mp4'",
            "detector=mediapipe"
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, cwd = "Visual_Speech_Recognition_for_Multiple_Languages")
        print("debug 2")
        print(result)
        print("debug 3")
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

        duration = ffmpeg.probe("Visual_Speech_Recognition_for_Multiple_Languages/uploaded_video/video.mp4")["format"]["duration"]
        print(duration)

        # asyncio.run(process_video())
        start_time = '00:00:00' # Start time for trimming (HH:MM:SS)
        end_time = '00:00:10' # End time for trimming (HH:MM:SS)

        frames = [
            ("00", "10"),
            ("10", "20"),
            ("20", "30")
        ]

        for frame in frames:
            start_time = f"00:00:{frame[0]}"
            end_time = f"00:00:{frame[1]}"
            (
                ffmpeg.input("Visual_Speech_Recognition_for_Multiple_Languages/uploaded_video/video.mp4", ss=start_time, to=end_time)
                .output(f"Visual_Speech_Recognition_for_Multiple_Languages/uploaded_video/processed_video_{frame[0]}_{frame[1]}.mp4")
                .run(overwrite_output=True)
            )
        
        start_time = f"00:00:00"
        (
            ffmpeg.input("Visual_Speech_Recognition_for_Multiple_Languages/uploaded_video/video.mp4", ss=start_time, to=end_time)
            .output(f"Visual_Speech_Recognition_for_Multiple_Languages/uploaded_video/processed_video.mp4")
            .run(overwrite_output=True)
        )
        
        subtitle_vtt_format = f"WEBVTT"

        # video -> subtitle_content
        for idx, frame in enumerate(frames):
            result = execute_model_infer(f"processed_video_{frame[0]}_{frame[1]}")
        
            subtitle = result["result"].split("hyp: ")[1]

            start = "0"
            end = "0"
            if idx*10 < 10:
                start = f"0{idx * 10}"
            else:
                start = f"{idx * 10}"
            
            end = f"{(idx+1) * 10}"
            subtitle_vtt_format += f"\n\n00:{start}.000 --> 00:{end}.000\n {subtitle}"

        print(subtitle_vtt_format)

        # Encode WebVTT content to base64
        subtitle_data = base64.b64encode(subtitle_vtt_format.encode('utf-8')).decode('utf-8')

        # Read the video file and encode it in base64
        with open("Visual_Speech_Recognition_for_Multiple_Languages/uploaded_video/processed_video.mp4", 'rb') as f:
            video_data = f.read()
            video_base64 = base64.b64encode(video_data).decode()

        # Respond with the base64-encoded video data
        return jsonify({'video_data': video_base64, "subtitle_data": subtitle_data})
    else:
        return jsonify({'error': 'No video file provided'}), 400

if __name__ == '__main__':
    app.run()
