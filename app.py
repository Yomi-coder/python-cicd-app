from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "Hello from CI/CD Pipeline!",
        "status":  "running",
        "version": os.getenv("APP_VERSION", "1.0.0")
    })

@app.route("/health")
def health():
    return jsonify({"status": "OK"}), 200

@app.route("/info")
def info():
    return jsonify({
        "app":         "myapp",
        "language":    "Python + Flask",
        "pipeline":    "Jenkins + Docker + Kubernetes",
        "environment": os.getenv("ENV", "development")
    })

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)