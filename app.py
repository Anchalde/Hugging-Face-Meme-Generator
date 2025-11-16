from flask import Flask, request, jsonify, send_from_directory, render_template_string
from flask_cors import CORS 
from backend import MemeGenerator
import os
import traceback

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)  
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 

GENERATED_MEMES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated_memes')
os.makedirs(GENERATED_MEMES_DIR, exist_ok=True)

generator = MemeGenerator()  

@app.route('/generate_meme', methods=['POST'])
def generate_meme():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        situation = data.get('situation')
        if not situation:
            return jsonify({"error": "No situation provided"}), 400
            
        style = data.get('style', 'cartoon') 
        
        filepath = generator.generate_complete_meme(situation, style)
        if filepath:
            relative_path = os.path.relpath(filepath, 'generated_memes')
            return jsonify({
                "message": "Meme generated successfully",
                "file_path": relative_path.replace('\\', '/')
            })
        else:
            return jsonify({"error": "Failed to generate meme"}), 500
    except Exception as e:
        print("Error generating meme:", str(e))
        traceback.print_exc()  # Print the full error traceback
        return jsonify({"error": str(e)}), 500

# Serve the frontend UI
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# Serve static files (JS, CSS, images)
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

# Serve generated meme images
@app.route('/meme/<filename>')
def serve_meme(filename):
    try:
        return send_from_directory(GENERATED_MEMES_DIR, filename, mimetype='image/png')
    except Exception as e:
        app.logger.error(f"Error serving meme {filename}: {str(e)}")
        return jsonify({"error": "Failed to serve image"}), 404

# Download meme images
@app.route('/download/<filename>')
def download_meme(filename):

    return send_from_directory(GENERATED_MEMES_DIR, filename, 
                            as_attachment=True,
                            mimetype='image/png',
                            download_name=filename)

if __name__ == '__main__':
    app.run(debug=True)
