import os
import sys
import shutil
import subprocess
from flask import Flask, request, redirect, send_file, render_template_string

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "member1", "images")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─────────────────────────────────────────
# UPLOAD PAGE
# ─────────────────────────────────────────
ERROR_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>GeoTrace — Error</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0d0d0d;
            color: #e0e0e0;
            font-family: 'Segoe UI', sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 24px;
        }
        .icon { font-size: 56px; margin-bottom: 24px; }
        .title {
            font-size: 22px;
            color: #ff4444;
            margin-bottom: 12px;
            font-weight: bold;
        }
        .detail {
            font-size: 14px;
            color: #666;
            max-width: 480px;
            line-height: 1.6;
            margin-bottom: 32px;
        }
        .back-btn {
            background: #00ffcc;
            color: #000;
            border: none;
            padding: 12px 28px;
            border-radius: 10px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            text-decoration: none;
        }
        .back-btn:hover { opacity: 0.85; }
        .tip {
            margin-top: 24px;
            font-size: 12px;
            color: #444;
            max-width: 440px;
            line-height: 1.6;
            border: 1px solid #222;
            border-radius: 8px;
            padding: 12px 16px;
            background: #111;
        }
        .tip b { color: #00ffcc; }
    </style>
</head>
<body>
    <div class="icon">📍</div>
    <div class="title">No GPS Data Found</div>
    <div class="detail">{{ error }}<br><br>{{ detail }}</div>
    <a href="/" class="back-btn">Try Again →</a>
    <div class="tip">
        <b>Tip:</b> GPS coordinates are embedded by your camera app automatically.
        Avoid WhatsApp, Instagram, or screenshot images — they strip this data.
        Use original photos from your phone's gallery.
    </div>
</body>
</html>
"""
UPLOAD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>GeoTrace — Upload Photos</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0d0d0d;
            color: #e0e0e0;
            font-family: 'Segoe UI', sans-serif;
            height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        .logo {
            font-size: 32px;
            font-weight: bold;
            color: #00ffcc;
            margin-bottom: 8px;
            letter-spacing: 2px;
        }

        .tagline {
            font-size: 13px;
            color: #555;
            margin-bottom: 48px;
            letter-spacing: 1px;
        }

        .upload-box {
            width: 560px;
            border: 2px dashed #333;
            border-radius: 16px;
            padding: 48px 32px;
            text-align: center;
            background: #111;
            transition: border-color 0.2s;
            cursor: pointer;
            position: relative;
        }

        .upload-box.dragover {
            border-color: #00ffcc;
            background: #0a1f1a;
        }

        .upload-icon {
            font-size: 48px;
            margin-bottom: 16px;
        }

        .upload-title {
            font-size: 18px;
            color: #fff;
            margin-bottom: 8px;
        }

        .upload-sub {
            font-size: 13px;
            color: #555;
            margin-bottom: 24px;
        }

        #file-input {
            display: none;
        }

        .browse-btn {
            background: #1a1a1a;
            border: 1px solid #333;
            color: #00ffcc;
            padding: 8px 20px;
            border-radius: 8px;
            font-size: 13px;
            cursor: pointer;
            letter-spacing: 0.5px;
        }

        .browse-btn:hover {
            border-color: #00ffcc;
        }

        .file-list {
            margin-top: 20px;
            text-align: left;
            max-height: 120px;
            overflow-y: auto;
        }

        .file-item {
            font-size: 12px;
            color: #888;
            padding: 4px 0;
            border-bottom: 1px solid #1a1a1a;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .file-item span { color: #00ffcc; }

        .track-btn {
            margin-top: 32px;
            width: 560px;
            padding: 16px;
            background: #00ffcc;
            color: #000;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            letter-spacing: 1px;
            transition: opacity 0.2s;
        }

        .track-btn:disabled {
            opacity: 0.3;
            cursor: not-allowed;
        }

        .track-btn:hover:not(:disabled) {
            opacity: 0.85;
        }

        .loading {
            display: none;
            margin-top: 24px;
            text-align: center;
        }

        .loading-text {
            font-size: 14px;
            color: #00ffcc;
            letter-spacing: 1px;
        }

        .spinner {
            width: 32px;
            height: 32px;
            border: 3px solid #222;
            border-top: 3px solid #00ffcc;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 12px auto 0;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .steps {
            margin-top: 12px;
            font-size: 12px;
            color: #555;
        }

        .steps span {
            display: block;
            padding: 2px 0;
            transition: color 0.3s;
        }

        .steps span.active {
            color: #00ffcc;
        }
    </style>
</head>
<body>

    <div class="logo">🌍 GeoTrace</div>
    <div class="tagline">Upload photos — we map the story hidden inside them</div>

    <form id="upload-form" action="/track" method="POST" enctype="multipart/form-data">
        <div class="upload-box" id="drop-zone">
            <div class="upload-icon">📸</div>
            <div class="upload-title">Drop your photos here</div>
            <div class="upload-sub">Supports JPG, JPEG, PNG with GPS metadata</div>
            <button type="button" class="browse-btn"
                onclick="document.getElementById('file-input').click()">
                Browse Files
            </button>
            <input type="file" id="file-input" name="images"
                   multiple accept=".jpg,.jpeg,.png">
            <div class="file-list" id="file-list"></div>
        </div>

        <button type="submit" class="track-btn" id="track-btn" disabled>
            Track Movement →
        </button>
    </form>

    <div class="loading" id="loading">
        <div class="spinner"></div>
        <div class="loading-text" style="margin-top:16px">
            Analyzing your photos...
        </div>
        <div class="steps" id="steps">
            <span id="s1">⏳ Extracting GPS metadata...</span>
            <span id="s2">⏳ Clustering locations...</span>
            <span id="s3">⏳ Analyzing movement patterns...</span>
            <span id="s4">⏳ Building intelligence map...</span>
        </div>
    </div>

    <script>
        const dropZone   = document.getElementById('drop-zone');
        const fileInput  = document.getElementById('file-input');
        const fileList   = document.getElementById('file-list');
        const trackBtn   = document.getElementById('track-btn');
        const form       = document.getElementById('upload-form');
        const loading    = document.getElementById('loading');
        let selectedFiles = [];

        // Drag and drop
        dropZone.addEventListener('dragover', e => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', e => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const files = Array.from(e.dataTransfer.files).filter(
                f => f.name.match(/\\.(jpg|jpeg|png)$/i)
            );
            addFiles(files);
        });

        // Browse
        fileInput.addEventListener('change', () => {
            addFiles(Array.from(fileInput.files));
        });

        function addFiles(files) {
            selectedFiles = [...selectedFiles, ...files];
            renderFileList();
        }

        function renderFileList() {
            fileList.innerHTML = '';
            selectedFiles.forEach(f => {
                const div = document.createElement('div');
                div.className = 'file-item';
                div.innerHTML = `<span>📷</span> ${f.name}
                    <span style="margin-left:auto;color:#555">
                        ${(f.size/1024).toFixed(1)} KB
                    </span>`;
                fileList.appendChild(div);
            });
            trackBtn.disabled = selectedFiles.length === 0;
            trackBtn.textContent = selectedFiles.length > 0
                ? `Track ${selectedFiles.length} Photo${selectedFiles.length > 1 ? 's' : ''} →`
                : 'Track Movement →';
        }

        // Submit
        form.addEventListener('submit', e => {
            e.preventDefault();

            if (selectedFiles.length === 0) return;

            // Build FormData with all files
            const formData = new FormData();
            selectedFiles.forEach(f => formData.append('images', f));

            // Show loading
            form.style.display  = 'none';
            loading.style.display = 'block';

            // Animate steps
            const steps = ['s1','s2','s3','s4'];
            let i = 0;
            const interval = setInterval(() => {
                if (i < steps.length) {
                    document.getElementById(steps[i]).classList.add('active');
                    document.getElementById(steps[i]).textContent =
                        document.getElementById(steps[i]).textContent.replace('⏳','✅');
                    i++;
                } else {
                    clearInterval(interval);
                }
            }, 2500);

            // Submit
            fetch('/track', {
    method: 'POST',
    body: formData
}).then(res => {
    if (res.redirected) {
        window.location.href = res.url;
    } else if (res.ok) {
        window.location.href = '/dashboard';
    } else {
        // Show error page content
        return res.text().then(html => {
            document.open();
            document.write(html);
            document.close();
        });
    }
}).catch(err => {
    alert('Error: ' + err);
    location.reload();
});
        });
    </script>

</body>
</html>
"""


# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(UPLOAD_HTML)


@app.route("/track", methods=["POST"])
def track():
    # 1 — Clear old images
   # 1 — Clear old images (delete files, not folder)
    if os.path.exists(UPLOAD_FOLDER):
        for f in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, f)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Could not delete {file_path}: {e}")
    else:
        os.makedirs(UPLOAD_FOLDER)

    # 2 — Save uploaded images
    files = request.files.getlist("images")
    for file in files:
        if file.filename:
            file.save(os.path.join(UPLOAD_FOLDER, file.filename))
# Clear old database so fresh data loads
    import sqlite3
    db_path = os.path.join(BASE_DIR, "member1", "metadata.db")
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.execute("DELETE FROM images")
        conn.commit()
        conn.close()
    # 3 — Run full pipeline
    member1_dir = os.path.join(BASE_DIR, "member1")
    member2_dir = os.path.join(BASE_DIR, "member2")
    member3_dir = os.path.join(BASE_DIR, "member3")
    member4_dir = os.path.join(BASE_DIR, "member4")

    # Member 1 — EXIF extraction
    subprocess.run([sys.executable, "main.py"], cwd=member1_dir, check=True)

    # Check if any valid GPS data was found
    output_json = os.path.join(member1_dir, "output_data.json")
    if os.path.exists(output_json):
        with open(output_json, "r") as f:
            import json
            extracted = json.load(f)
        if len(extracted) == 0:
            return render_template_string(ERROR_HTML, 
                error="None of the uploaded images contain GPS coordinates.",
                detail="This usually happens with WhatsApp photos (EXIF stripped) or screenshots. Please upload original camera photos."
            ), 400
    else:
        return render_template_string(ERROR_HTML,
            error="Pipeline failed — no output generated.",
            detail="Please try again with different photos."
        ), 400

    # Member 2 — Clustering
    subprocess.run([sys.executable, "cluster.py"], cwd=member2_dir, check=True)

    # Member 3 — Movement analysis
    subprocess.run([sys.executable, "member3_movement.py"], cwd=member3_dir, check=True)

    # Member 4 — Dashboard generation
    subprocess.run([sys.executable, "member4_dashboard.py"], cwd=member4_dir, check=True)

    return redirect("/dashboard")


@app.route("/dashboard")
def dashboard():
    dashboard_path = os.path.join(BASE_DIR, "member4", "dashboard.html")
    return send_file(dashboard_path)


@app.route("/map.html")
def map_file():
    map_path = os.path.join(BASE_DIR, "member4", "map.html")
    return send_file(map_path)


# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=5000)