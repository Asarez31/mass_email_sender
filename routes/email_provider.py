import os
import json
from flask import Blueprint, render_template, request, jsonify

email_provider_bp = Blueprint("email_provider", __name__)

CONFIG_FILE = os.path.join("config", "email_provider.json")

# Ensure config directory exists
os.makedirs("config", exist_ok=True)

def load_provider_settings():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_provider_settings(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


@email_provider_bp.route("/", methods=["GET"])
def index():
    """Render the email provider settings page with saved config"""
    settings = load_provider_settings()
    return render_template("index.html", settings=settings)


@email_provider_bp.route("/save", methods=["POST"])
def save_provider():
    """Save provider settings permanently"""
    data = request.json
    if not data.get("provider"):
        return jsonify({"error": "Provider is required"}), 400

    save_provider_settings(data)
    return jsonify({"message": "Settings saved successfully"})


@email_provider_bp.route("/test", methods=["POST"])
def test_email():
    """Send a test email (placeholder for now)"""
    data = request.json
    # TODO: integrate Gmail/Outlook/SMTP send test here
    return jsonify({"message": f"Test email sent to {data.get('test_email', '')}"})