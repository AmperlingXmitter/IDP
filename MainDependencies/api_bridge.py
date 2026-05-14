from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import threading
import os

app = Flask(__name__)
CORS(app)

trigger_requested = False

latest_data = {
    "status": "",
    "timestamp": "",
    "percentage": 0,
    "grade": "",
    "confidence": 0,
    "original_image": "",
    "segmented_image": "",
    "overlayed_image": ""
}

#--------------------SETUP SERVER--------------------

def run_server():
    # Run on port 5000, host 0.0.0.0 makes it visible on the local network
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def start_api():
    threading.Thread(target=run_server, daemon=True).start()

#--------------------DATA TRANSFER FUNCTIONS--------------------

@app.route('/trigger_scan', methods=['POST', 'GET'])
def trigger_scan():
    global trigger_requested
    
    try:
        trigger_requested = True
        return jsonify(latest_data)
    except Exception as error_text:
        return jsonify({"status": "Error: Trigger Scan", "message": str(error_text)}), 500

@app.route('/get_data', methods=['GET'])
def get_data():
    return jsonify(latest_data)

@app.route('/get_image', methods=['GET'])
def get_image():
    image_type = request.args.get('type', 'original')
    
    # Map the type to the correct key in latest_data
    # Use the keys that run_full_process actually returns
    type_to_key = {
        "original": "original_image",
        "segmented": "segmented_image",
        "overlayed": "overlayed_image"
    }
    
    target_key = type_to_key.get(image_type, "original_image")
    image_path = latest_data.get(target_key, "")
    
    if image_path and os.path.isfile(image_path):
        try:
            return send_file(image_path, mimetype='image/jpeg')
        except Exception as error_text:
            return f"Error sending file: {str(error_text)}", 500
            
    return f"Image type '{image_type}' not found", 404

