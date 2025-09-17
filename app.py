from flask import Flask, render_template, request, jsonify
import os, json

app = Flask(__name__)

CONFIG_FILE = os.path.join("config", "email_provider.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(data):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/provider/settings", methods=["GET", "POST"])
def provider_settings():
    if request.method == "GET":
        return jsonify(load_config())

    elif request.method == "POST":
        data = request.json
        save_config(data)
        return jsonify({"message": "Settings saved successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)