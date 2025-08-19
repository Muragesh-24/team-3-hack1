from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import os
app = Flask(__name__)
API_KEY = "AIzaSyC3rfrN9Z9Dw3-LRh37JAksXLkOUsJBETg"
client = genai.Client(api_key=API_KEY)
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/generate_story', methods=['POST'])
def generate_story():
    data = request.get_json()
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({'story': 'No prompt provided.'})




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

    for idx, line in enumerate(dialogue_lines):
        result_html += f"<div style='margin-bottom:8px;'><b>{line}</b></div>"
        result_html += f'<div id="image-{idx}" style="margin-bottom:16px; text-align:center; color:#666;">Loading image...</div>'

    return jsonify({'story': result_html, 'dialogue_lines': dialogue_lines, 'original_prompt': prompt})

@app.route('/generate_images', methods=['POST'])
def generate_images():
    data = request.get_json()
    dialogue_lines = data.get('dialogue_lines', [])
    original_prompt = data.get('original_prompt', '')
    line_index = data.get('line_index', 0)
    
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
                break
    except Exception as e:
        print(f"Error generating image for line {line_index}: {e}")
        return jsonify({'error': f'Failed to generate image: {str(e)}'})

    return jsonify({'image': image_b64, 'line_index': line_index})

if __name__ == '__main__':
    app.run(debug=True)