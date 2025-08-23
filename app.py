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
import shutil
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip, concatenate_audioclips

# --- Story Audio Generation Class (Integrated) ---
class StoryAudioGenerator:
    """
    A class to dynamically convert a story text with character tags into a single
    audio file, assigning different voices to characters as they are discovered.
    """
    def __init__(self, output_dir="generated_audio"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.available_voices = [
            {"language": "en-us"}, {"language": "en-gb"},
            {"language": "en-au"}, {"language": "en-in"},
        ]
        self.voice_idx = 0
        self.assigned_voices = {}

    def _get_voice_for_character(self, character_name):
        if character_name in self.assigned_voices:
            return self.assigned_voices[character_name]
        voice_to_assign = self.available_voices[self.voice_idx]
        self.assigned_voices[character_name] = voice_to_assign
        self.voice_idx = (self.voice_idx + 1) % len(self.available_voices)
        print(f"  - New character found: '{character_name}'. Assigning voice: {voice_to_assign['language']}")
        return voice_to_assign

    def _split_story_by_character(self, text):
        segments = []
        lines = text.strip().split('\n')
        for line in lines:
            if line.strip() and ':' in line:
                parts = line.split(':', 1)
                character = parts[0].strip().strip('[]')
                dialogue = parts[1].strip()
                segments.append({"character": character, "text": dialogue})
        return segments

    def _generate_audio_for_segments(self, segments):
        audio_clips = []
        print("\nGenerating audio for each story segment...")
        for i, segment in enumerate(segments):
            character = segment["character"]
            text = segment["text"]
            voice_config = self._get_voice_for_character(character)
            lang = voice_config["language"]
            audio_path = os.path.join(self.output_dir, f"segment_{i:03d}.mp3")
            try:
                tts = gTTS(text=text, lang=lang, slow=False)
                tts.save(audio_path)
                clip = AudioFileClip(audio_path)
                audio_clips.append(clip)
            except Exception as e:
                print(f"    - Error generating audio for segment {i+1}: {e}")
        return audio_clips

    def cleanup(self):
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
            print(f"Cleaned up temporary directory: {self.output_dir}")

    def generate_story_audio(self, story_text):
        print("Starting audio generation process...")
        self.assigned_voices = {}
        self.voice_idx = 0
        story_segments = self._split_story_by_character(story_text)
        if not story_segments:
            return None
        
        # With moviepy, we don't need to generate separate clips first
        full_audio_path = os.path.join(self.output_dir, "final_story_audio.mp3")
        
        # Create a list of audio file paths
        segment_paths = []
        for i, segment in enumerate(story_segments):
            character = segment["character"]
            text = segment["text"]
            voice_config = self._get_voice_for_character(character)
            lang = voice_config["language"]
            audio_path = os.path.join(self.output_dir, f"segment_{i:03d}.mp3")
            try:
                tts = gTTS(text=text, lang=lang, slow=False)
                tts.save(audio_path)
                segment_paths.append(audio_path)
            except Exception as e:
                print(f"    - Error generating audio for segment {i+1}: {e}")

        # Concatenate audio files using moviepy
        if segment_paths:
            clips = [AudioFileClip(p) for p in segment_paths]
            final_audio = concatenate_audioclips(clips)
            final_audio.write_audiofile(full_audio_path, codec="mp3")
            final_audio.close()
            for clip in clips:
                clip.close()
            return full_audio_path
        return None


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
    story_text = session_data['story_text']

    audio_generator = StoryAudioGenerator(output_dir=f"temp_audio_{session_id}")
    audio_path = audio_generator.generate_story_audio(story_text)
    
    if not audio_path or not os.path.exists(audio_path):
        return jsonify({'error': 'Failed to generate audio for the story.'})
        
    # --- Step 2: Create a timed, silent video from images ---
    video_without_audio_path = f"videos/{session_id}_silent.mp4"
    final_video_path = f"videos/{session_id}_story_video.mp4"
    
    try:
        # Get all image paths in order
        image_paths = []
        for i in range(len(session_data['dialogue_lines'])):
            if i in session_data['images']:
                image_paths.append(session_data['images'][i])
        
        if not image_paths:
            return jsonify({'error': 'No images available for video creation'})
        
        audio_clip_for_duration = AudioFileClip(audio_path)
        audio_duration = audio_clip_for_duration.duration
        audio_clip_for_duration.close()
        duration_per_image = audio_duration / len(image_paths)

        target_size = (512, 512) 
        fps = 24 
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(video_without_audio_path, fourcc, fps, target_size)

        resized_images = []
        frames_per_image = int(duration_per_image * fps)

        for img_path in image_paths:
            img = cv2.imread(img_path)
            if img is not None:
                img_resized = cv2.resize(img, target_size)
                resized_images.append(img_resized)
                for _ in range(frames_per_image):
                    video_writer.write(img_resized)
        video_writer.release()
        
        if not resized_images:
            return jsonify({'error': 'Failed to process images'})

        video_filename = f"videos/{session_id}_story_video.mp4"
        
        video_clip = VideoFileClip(video_without_audio_path)
        audio_clip = AudioFileClip(audio_path)
        
        final_clip = video_clip.set_audio(audio_clip)
        final_clip.write_videofile(final_video_path, codec='libx264', audio_codec='aac')
        
        final_clip.close()
        video_clip.close()
        audio_clip.close()
        audio_generator.cleanup()
        if os.path.exists(video_without_audio_path):
            os.remove(video_without_audio_path)
        return jsonify({
            'success': True, 
            'video_path': final_video_path,
            'message': f'Video created successfully with {len(resized_images)} images and audio'
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