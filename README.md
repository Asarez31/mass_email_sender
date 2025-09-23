# Mass Email Sender

Mass Email Sender is a web-based application for creating, managing, and sending personalized email campaigns to multiple recipients. It supports uploading recipient lists via CSV/XLSX, composing emails with dynamic fields, and integrates with configurable email providers.

## Features

- **Create Campaigns:** Compose email subject and body, with support for personalization using placeholders (e.g., `{Name}`).
- **Upload Recipients:** Import recipient lists from CSV or XLSX files.
- **Preview & Review:** Review campaign details before sending.
- **Configurable Providers:** Easily switch between email providers via configuration.
- **Responsive UI:** Built with Tailwind CSS for a modern, responsive interface.

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- (Optional) Virtual environment

### Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/mass_email_sender.git
   cd mass_email_sender
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure email provider:**
   - Edit `config/email_provider.json` with your provider credentials.
   - **Note:** This file is ignored by git for security.

### Running the App

```sh
python app.py
```

Visit [http://localhost:5000](http://localhost:5000) in your browser.

## Usage

1. **Create a Campaign:** Enter the subject and body of your email. In the body you can add placeholders es. {Name}, {Address} etc.
2. **Upload Recipients:** Select a CSV/XLSX file with recipient details. Placeholders are to be defined in the uploaded file
3. **Review & Send:** Confirm details and send your campaign.

## File Structure

```
mass_email_sender/
├── app.py
├── config/
│   └── email_provider.json
├── templates/
│   └── index.html
├── static/
│   └── img/
├── requirements.txt
└── README.md
```

## Security

- Sensitive configuration files (like `email_provider.json`) are excluded from version control via `.gitignore`.

## License

MIT License

## Author

Jacob Asare

---

*For questions or contributions, please open an issue or submit a pull request.*