from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory

from model_loader import NextPagePredictor
import json

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
PAGES_CONFIG_PATH = BACKEND_DIR / "pages_config.json" 

# Load pages config
if PAGES_CONFIG_PATH.exists():
  with open(PAGES_CONFIG_PATH, "r") as f:
    PAGES_CONFIG = json.load(f)
else:
  PAGES_CONFIG = {}
  print("Warning: pages_config.json not found.")

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path=""
)

SESSION_HISTORY = {}

PREDICTOR = None
try:
    PREDICTOR = NextPagePredictor()
    print("[PP] NextPagePredictor loaded.")
except Exception as e:
    print(f"[PP] NextPagePredictor not active: {e}")

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def static_files(path):
    target = FRONTEND_DIR / path
    if target.is_file():
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/api/event", methods=["POST"])
def log_event():
    data = request.get_json(silent=True) or {}

    session_id = str(data.get("session_id", "")).strip() or "anon"
    current_page = str(data.get("current_page", "")).strip()

    if not current_page:
        return jsonify({"error": "current_page is required"}), 400

    history = SESSION_HISTORY.get(session_id, [])
    history.append(current_page)
    SESSION_HISTORY[session_id] = history

    predicted_pages = []
    if PREDICTOR is not None:
        try:
            predicted_pages = PREDICTOR.predict_top_k(history, k=2)
        except Exception as e:
            print(f"[PP] prediction error: {e}")
            predicted_pages = []

        response_body = {
        "status": "ok",
        "session_id": session_id,
        "current_page": current_page,
        "history_length": len(history),
        "predicted_pages": predicted_pages
        }

        resp = jsonify(response_body)

        # Add Link header with prefetch/preload hints if we have predictions
        link_header = build_link_header(predicted_pages)
        if link_header:
            resp.headers["Link"] = link_header
            print(f"[PP] Link header set: {link_header}")

        return resp

def build_link_header(predicted_pages):
    if not predicted_pages:
        return None

    links = []

    for page in predicted_pages:
        cfg = PAGES_CONFIG.get(page)
        if not cfg:
            continue

        # Prefetch the HTML document
        url = cfg.get("url")
        if url:
            links.append(f"<{url}>; rel=prefetch")

        # Preload key assets
        for asset in cfg.get("assets", []):
            links.append(f"<{asset}>; rel=preload")

    if not links:
        return None

    return ", ".join(links)

if __name__ == "__main__":
    # Development Server
    # For HTTP/2, run this app with Hypercorn (instructed in README)
    app.run(host="0.0.0.0", port=5000, debug=True)
