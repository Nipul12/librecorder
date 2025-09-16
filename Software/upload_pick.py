from tkinter import Tk, filedialog
import requests, os
from mimetypes import guess_type

Tk().withdraw()
path = filedialog.askopenfilename(
    title="Choose a JPG or TXT",
    filetypes=[("JPEG images","*.jpg *.jpeg"), ("Text files","*.txt"), ("All files","*.*")]
)
if path:
    mime, _ = guess_type(path)
    if mime is None:
        mime = "application/octet-stream"
    with open(path, "rb") as f:
        r = requests.post(
            "http://127.0.0.1:8000/upload",
            files={"file": (os.path.basename(path), f, mime)},
            timeout=60
        )
    print("Uploaded:", r.status_code, r.text)
