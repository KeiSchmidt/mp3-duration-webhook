# main.py
from flask import Flask, request, jsonify, Response
import os
import requests
from mutagen.mp3 import MP3
from io import BytesIO

app = Flask(__name__)

@app.route("/")
def home():
    return "Webhook active!", 200

# Lark events (verification)
@app.route("/lark-event", methods=["POST"])
def lark_event():
    try:
        data = request.get_json(force=True, silent=True) or {}
    except Exception:
        data = {}

    # Lark subscription verification: nếu có key "challenge" -> trả về JSON { "challenge": "..." }
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    # log event cho debug
    app.logger.info("Lark event received: %s", data)
    return jsonify({"status": "ok"})

# Endpoint lấy duration từ URL (POST JSON: {"file_url": "https://..."})
@app.route("/get-duration", methods=["POST"])
def get_duration():
    j = request.get_json(force=True, silent=True) or {}
    file_url = j.get("file_url")
    if not file_url:
        return jsonify({"error": "file_url required"}), 400
    try:
        # tải file (small files). Nếu file lớn hoặc cần auth, xử lý khác.
        r = requests.get(file_url, timeout=30, stream=True)
        r.raise_for_status()
        data = r.content
        audio = MP3(BytesIO(data))
        duration = audio.info.length  # seconds (float)
        # trả về giây làm số nguyên hoặc float
        return jsonify({"duration_seconds": round(duration, 2)})
    except Exception as e:
        app.logger.exception("Error getting duration")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
