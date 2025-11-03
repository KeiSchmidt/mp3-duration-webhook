from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Webhook active!", 200

@app.route("/lark-event", methods=["POST"])
def lark_event():
    data = request.get_json(force=True)
    print("Received data:", data)

    # ✅ Khi Lark gửi challenge để xác minh webhook
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    # ✅ Các event khác (ví dụ thêm bản ghi, sửa bản ghi)
    return jsonify({"msg": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

