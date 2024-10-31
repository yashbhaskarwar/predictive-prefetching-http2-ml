from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory

from model_loader import NextPagePredictor  # NEW

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

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

    return jsonify({
        "status": "ok",
        "session_id": session_id,
        "current_page": current_page,
        "history_length": len(history),
        "predicted_pages": predicted_pages
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
