import os, sys, signal
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename

# --- config ---
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED = {"jpg", "jpeg","txt"}               # only JPG/JPEG/txt 
MAX_MB = 20

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__) 
app.config["MAX_CONTENT_LENGTH"] = MAX_MB * 1024 * 1024   #maximum size of file <20MB

def allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED

# --- endpoints ---
@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify(error="no file part"), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify(error="no selected file"), 400
    if not allowed(f.filename):
        return jsonify(error="only .jpg/.jpeg allowed"), 400

    ts = datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")
    safe = secure_filename(f.filename)
    name = f"{ts}-{safe}"
    #S3 code
    path = os.path.join(UPLOAD_DIR, name)
    f.save(path)
    print(f"[save] {path} ({os.path.getsize(path)} bytes)")
    return jsonify(message="ok", filename=name, url=f"/files/{name}")

@app.route("/files/<path:name>", methods=["GET"])
def get_file(name):
    return send_from_directory(UPLOAD_DIR, name, as_attachment=False)

@app.route("/list", methods=["GET"])
def list_files():
    return jsonify(sorted(os.listdir(UPLOAD_DIR)))

@app.route("/gallery", methods=["GET"])
def gallery():
    cards = []
    for name in sorted(os.listdir(UPLOAD_DIR)):
        cards.append(f"""
        <div style="display:inline-block;margin:8px;text-align:center">
          <a href="/files/{name}" target="_blank">
            <img src="/files/{name}" style="max-width:200px;border:1px solid #ccc;display:block"/>
          </a>
          <small>{name}</small>
        </div>""")
    return f"<!doctype html><h1>Uploads</h1>{''.join(cards)}"

# --- make Ctrl+C reliable on Windows ---
def _graceful_exit(sig, frame):
    print("\n[shutdown] Caught Ctrl+C, exiting...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, _graceful_exit)
    app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=False)

