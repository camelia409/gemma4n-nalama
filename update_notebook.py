import json

with open("nalama-gemma4-tamil-fixed.ipynb", "r", encoding="utf-8") as f:
    nb = json.load(f)

# Add a markdown cell to explain uploading the frontend
intro_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## Hosting the Frontend\\n",
        "1. Build your Vite React app using `npm run build` locally.\\n",
        "2. Zip the `dist` folder created into `dist.zip`.\\n",
        "3. Upload `dist.zip` to your Kaggle datasets and note the path.\\n",
        "4. Unzip here using exactly the path where it was uploaded (e.g. `!unzip -o /kaggle/input/nalam-frontend/dist.zip -d /kaggle/working/dist`).\\n",
        "Once done, the Flask app below will serve it automatically!"
    ]
}

# Find the Flask cell and modify it
for cell in nb["cells"]:
    code = "".join(cell.get("source", []))
    if "Flask API" in code:
        new_flask_init = """
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
import base64
import io
import os

# Set static_folder to the extracted React dist directory
FRONTEND_DIST = '/kaggle/working/dist'

app = Flask(__name__, static_folder=FRONTEND_DIST, static_url_path='/')
CORS(app)

# --- Frontend Routes ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
# -----------------------
"""
        code = code.replace(
            "from flask import Flask, request, jsonify\nfrom flask_cors import CORS\nimport numpy as np\nimport base64\nimport io\n\napp = Flask(__name__)\nCORS(app)",
            new_flask_init.strip()
        )
        cell["source"] = [code]

# Insert the markdown cell before the Flask cell
flask_idx = 0
for i, cell in enumerate(nb["cells"]):
    if "Flask API" in "".join(cell.get("source", [])):
        flask_idx = i
        break

nb["cells"].insert(flask_idx, intro_cell)

with open("nalama-gemma4-tamil-fixed-hosted.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print("Updated notebook saved as nalama-gemma4-tamil-fixed-hosted.ipynb")
