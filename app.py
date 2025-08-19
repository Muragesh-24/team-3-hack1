from flask import Flask, render_template, request, jsonify, send_file
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import os
import cv2
import numpy as np
import uuid
import json
app = Flask(__name__)
API_KEY = "AIzaSyC3rfrN9Z9Dw3-LRh37JAksXLkOUsJBETg"
client = genai.Client(api_key=API_KEY)

# Create directories for storing images and videos
os.makedirs('temp_images', exist_ok=True)
os.makedirs('videos', exist_ok=True)


story_sessions = {}
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/generate_story', methods=['POST'])
def generate_story():
    data = request.get_json()
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({'story': 'No prompt provided.'})

    session_id = str(uuid.uuid4())

    # Generate story as only dialogue between at most 4 entities
    story_prompt = (
        f"Write a short story based only on dialogue exchanges between at most 4 entities (characters, animals, or objects) for the following prompt. "
        f"The story should be in script format, with each line as 'Name: \"Dialogue\"'. Do not include any narration, scene descriptions, or action text. "
        f"The story should be concise, but at least 10 dialogues per entity and meaningful , i.e the dialogue should convey the essence of the story without unnecessary elaboration."
        f"No more than 4 entities. Each entity should have a distinct name. Keep the story concise and focused on their conversation.\n\nPrompt: \"{prompt}\""
    )

    story_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=story_prompt
    )
    story_text = story_response.candidates[0].content.parts[0].text

    #dialogue lines
    dialogue_lines = [line.strip() for line in story_text.split('\n') if line.strip()]
    result_html = ""

    # Store session data
    story_sessions[session_id] = {
        'prompt': prompt,
        'dialogue_lines': dialogue_lines,
        'images': {},
        'story_text': story_text
    }

    for idx, line in enumerate(dialogue_lines):
        result_html += f"<div style='margin-bottom:8px;'><b>{line}</b></div>"
        result_html += f'<div id="image-{idx}" style="margin-bottom:16px; text-align:center; color:#666;">Loading image...</div>'

    # Add video creation button
    result_html += f'<br><button onclick="createVideo(\'{session_id}\')" style="padding:10px 20px; background:#28a745; color:white; border:none; border-radius:5px; cursor:pointer;">Create Video</button>'
    result_html += f'<div id="video-status" style="margin-top:10px;"></div>'

    return jsonify({'story': result_html, 'dialogue_lines': dialogue_lines, 'original_prompt': prompt, 'session_id': session_id})

@app.route('/generate_images', methods=['POST'])
def generate_images():
    data = request.get_json()
    dialogue_lines = data.get('dialogue_lines', [])
    original_prompt = data.get('original_prompt', '')
    line_index = data.get('line_index', 0)
    session_id = data.get('session_id', '')
    
    if line_index >= len(dialogue_lines):
        return jsonify({'error': 'Invalid line index'})
    
    line = dialogue_lines[line_index]
    
    # Generate an image for this specific line
    image_prompt = f"Create an illustration for this scene from the story '{original_prompt}': {line}"
    image_b64 = None
    try:
        image_response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=image_prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )
        for part in image_response.candidates[0].content.parts:
            if part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                image_b64 = base64.b64encode(buffered.getvalue()).decode()
                
                # Save image to disk for video creation
                if session_id and session_id in story_sessions:
                    image_filename = f"temp_images/{session_id}_{line_index:03d}.png"
                    image.save(image_filename)
                    story_sessions[session_id]['images'][line_index] = image_filename
                
                break
    except Exception as e:
        print(f"Error generating image for line {line_index}: {e}")
        return jsonify({'error': f'Failed to generate image: {str(e)}'})

    return jsonify({'image': image_b64, 'line_index': line_index})

@app.route('/create_video', methods=['POST'])
def create_video():
    data = request.get_json()
    session_id = data.get('session_id', '')
    
    if session_id not in story_sessions:
        return jsonify({'error': 'Invalid session ID'})
    
    session_data = story_sessions[session_id]
    
    try:
        # Get all image paths in order
        image_paths = []
        for i in range(len(session_data['dialogue_lines'])):
            if i in session_data['images']:
                image_paths.append(session_data['images'][i])
        
        if not image_paths:
            return jsonify({'error': 'No images available for video creation'})
        target_size = (512, 512) 
        resized_images = []
        
        for img_path in image_paths:
            img = cv2.imread(img_path)
            if img is not None:
                img_resized = cv2.resize(img, target_size)
                resized_images.append(img_resized)
        
        if not resized_images:
            return jsonify({'error': 'Failed to process images'})

        video_filename = f"videos/{session_id}_story_video.mp4"
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = 1 
        video_writer = cv2.VideoWriter(video_filename, fourcc, fps, target_size)
        
        for img in resized_images:

            video_writer.write(img)
        
        video_writer.release()
        
        return jsonify({
            'success': True, 
            'video_path': video_filename,
            'message': f'Video created successfully with {len(resized_images)} images'
        })
        
    except Exception as e:
        print(f"Error creating video: {e}")
        return jsonify({'error': f'Failed to create video: {str(e)}'})

@app.route('/download_video/<session_id>')
def download_video(session_id):
    video_filename = f"videos/{session_id}_story_video.mp4"
    if os.path.exists(video_filename):
        return send_file(video_filename, as_attachment=True, download_name=f"story_{session_id}.mp4")
    else:
        return jsonify({'error': 'Video not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)