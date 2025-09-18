import os
import json
import smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "email_provider.json")

# Ensure config folder exists
os.makedirs(CONFIG_DIR, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/templates/settings.html")
def settings():
    return render_template("settings.html")

@app.route("/templates/review.html")
def review():
    return render_template("review.html")


@app.route("/api/settings/provider", methods=["POST"])
def save_provider_settings():
    try:
        data = request.json
        provider = data.get("provider")
        default_email = data.get("default_email")
        credentials = data.get("credentials")

        if not provider or not isinstance(credentials, dict) or not credentials:
            return jsonify({"error": "Provider and Settings are required"}), 400

        settings = {
            "provider": provider,
            "default_email": default_email,
            "credentials": credentials
        }

        # Save to config/email_provider.json
        with open(CONFIG_FILE, "w") as f:
            json.dump(settings, f, indent=4)

        return jsonify({"message": "✅ API key saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/settings/provider", methods=["GET"])
def get_provider_settings():
    try:
        if not os.path.exists(CONFIG_FILE):
            return jsonify({"message": "No provider settings found"}), 404

        with open(CONFIG_FILE, "r") as f:
            settings = json.load(f)

        return jsonify(settings), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/send_test_email", methods=["POST"])
def send_test_email():
    try:
        if not os.path.exists(CONFIG_FILE):
            return jsonify({"error": "No provider settings found"}), 400

        with open(CONFIG_FILE, "r") as f:
            settings = json.load(f)

        provider = settings.get("provider")
        credentials = settings.get("credentials", {})
        recipient = settings.get("default_email")

        if provider == "gmail":
            sender_email = credentials.get("gmail_email")

        elif provider == "outlook":
            sender_email = credentials.get("client_id")

        elif provider == "smtp":
            sender_email = credentials.get("smtp_username")

        if not sender_email:
            return jsonify({"error": "No default sender email configured"}), 400

        if not recipient:
            return jsonify({"error": "No default test email configured"}), 400

        # Create the email
        msg = MIMEText("This is a test email from AsarezMail")
        msg["Subject"] = "Test Email - AsarezMail"
        msg["From"] = sender_email
        msg["To"] = recipient

        # Handle providers
        if provider == "gmail":
            # Simplified: use SMTP with Gmail
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, credentials.get("api_key"))
                server.send_message(msg)

        elif provider == "outlook":
            with smtplib.SMTP("smtp.office365.com", 587) as server:
                server.starttls()
                server.login(credentials.get("client_id"),
                             credentials.get("client_secret"))
                server.send_message(msg)

        elif provider == "smtp":
            host = credentials.get("smtp_host")
            port = int(credentials.get("smtp_port", 587))
            username = credentials.get("smtp_username")
            password = credentials.get("smtp_password")

            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)

        else:
            return jsonify({"error": "Unsupported provider"}), 400

        return jsonify({"message": f"Test email sent successfully to {recipient}!"}), 200
    
    except Exception as e:
        return jsonify({
        "api_key": credentials.get("api_key") if credentials else None,
        "error": str(e)
    }), 500



if __name__ == "__main__":
    app.run(debug=True)
