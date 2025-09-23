import os, re, json, pandas as pd, smtplib
from email.mime.text import MIMEText
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "email_provider.json")
CAMPAIGN_FILE = os.path.join(CONFIG_DIR, "campaign.json")

# Ensure config folder exists
os.makedirs(CONFIG_DIR, exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/settings")
def settings():
    return render_template("settings.html")


@app.route("/review")
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


@app.route("/api/send_email", methods=["POST"])
def send_email():
    """
    Handles both test and campaign emails.
    Request JSON:
    {
      "mode": "test" | "campaign"
    }
    """
    try:
        if not os.path.exists(CONFIG_FILE):
            return jsonify({"error": "No provider settings found"}), 400

        with open(CONFIG_FILE, "r") as f:
            settings = json.load(f)

        provider = settings.get("provider")
        credentials = settings.get("credentials", {})
        sender_email = None

        if provider == "gmail":
            sender_email = credentials.get("gmail_email")
        elif provider == "outlook":
            sender_email = credentials.get("client_id")
        elif provider == "smtp":
            sender_email = credentials.get("smtp_username")

        if not sender_email:
            return jsonify({"error": "No default sender email configured"}), 400

        # Get request mode
        data = request.json or {}
        mode = (data.get("mode") or "").lower().strip()
        print("Mode received:", repr(mode))

        if mode == "test":
            recipient = settings.get("default_email")
            if not recipient:
                return jsonify({"error": "No default test email configured"}), 400

            msg = MIMEText("This is a test email from AsarezMail")
            msg["Subject"] = "Test Email - AsarezMail"
            msg["From"] = sender_email
            msg["To"] = recipient

            send_via_provider(provider, credentials, msg,
                              sender_email, recipient)
            return jsonify({"message": f"Test email sent successfully to {recipient}!"}), 200

        elif mode == "campaign":
            if not os.path.exists(CAMPAIGN_FILE):
                return jsonify({"error": "No campaign data found"}), 400

            with open(CAMPAIGN_FILE, "r") as f:
                campaign = json.load(f)

            subject = campaign.get("subject", "No Subject")
            body_template = campaign.get("body", "")
            recipients = campaign.get("recipients", [])

            sent_count = 0
            for r in recipients:
                email = r.get("Email") or r.get("email")
                if not email:
                    continue

                # Start with template
                body = body_template

                # Replace all placeholders dynamically (case-insensitive)
                for key, value in r.items():
                    pattern = re.compile(r"\{" + re.escape(key) + r"\}", re.IGNORECASE)
                    body = pattern.sub(str(value or ""), body)

                msg = MIMEText(body, "html")  # HTML-safe
                msg["Subject"] = subject
                msg["From"] = sender_email
                msg["To"] = email

                send_via_provider(provider, credentials, msg, sender_email, email)
                sent_count += 1

            return jsonify({"message": f"Campaign sent to {sent_count} recipients!"}), 200

        else:
            return jsonify({"error": "Invalid mode"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def send_via_provider(provider, credentials, msg, sender_email, recipient):
    """Handles sending via Gmail, Outlook, or SMTP"""
    if provider == "gmail":
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


@app.route("/api/save_campaign", methods=["POST"])
def save_campaign():
    try:
        data = request.json
        subject = data.get("subject")
        body = data.get("body")
        recipients = data.get("recipients", [])

        if not subject or not body:
            return jsonify({"success": False, "message": "Subject and body required"}), 400

        campaign_data = {
            "subject": subject,
            "body": body,
            "recipients": recipients
        }

        with open(CAMPAIGN_FILE, "w") as f:
            json.dump(campaign_data, f, indent=4)

        return jsonify({"success": True, "message": "Campaign saved successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/api/upload_recipients", methods=["POST"])
def upload_recipients():
    try:
        file = request.files["file"]
        if not file:
            return jsonify({"success": False, "message": "No file uploaded"}), 400

        ext = os.path.splitext(file.filename)[1].lower()
        if ext == ".csv":
            df = pd.read_csv(file)
        elif ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            return jsonify({"success": False, "message": "Invalid file type"}), 400

        # Expect columns like: Email, Name, {Placeholder1}, {Placeholder2}
        recipients = df.to_dict(orient="records")

        return jsonify({"success": True, "recipients": recipients, "count": len(recipients)})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/get_campaign", methods=["GET"])
def get_campaign():
    if not os.path.exists(CAMPAIGN_FILE):
        return jsonify({"error": "No campaign data found"}), 404

    with open(CAMPAIGN_FILE, "r") as f:
        campaign = json.load(f)

    return jsonify(campaign)


if __name__ == "__main__":
    app.run(debug=True)
