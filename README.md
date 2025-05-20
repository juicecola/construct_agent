
# 🏗️ ConstructAgent 
This is the **backend service** for the **ConstructAgent**, a smart assistant built for construction sites to streamline hazard logging, worker attendance, and material delivery notifications via **SMS/USSD** using **Africa's Talking** and **Dialogflow CX**.

---

## 🧠 Core Features

- 📲 **SMS/USSD Interaction**: Handles messages via Africa's Talking's API.
- 🗣️ **Natural Language Understanding**: Integrates with Google Dialogflow CX for NLP-based intent recognition.
- ⚠️ **Hazard Logging**: Records safety-related messages.
- ✅ **Attendance Check-in**: Logs worker attendance.
- 📦 **Delivery Tracking**: Tracks material delivery updates.
- 📤 **Auto-Response & Alerts**: Sends confirmation and admin alerts via SMS.

---

## 🗂️ Project Structure

```
construct_agent_hackathon/
├── backend/
│   ├── app.py                # Main Flask application
│   ├── test_sms.py           # (Optional) Script to simulate SMS sending
│   ├── requirements.txt      # Backend dependencies
│   ├── gcp-key.json          # Google credentials for Dialogflow CX (DO NOT SHARE)
│   └── venv/                 # Python virtual environment
└── frontend/                 # Frontend app (React) – not covered here
```

---

## 🚀 Getting Started

### ✅ Prerequisites

- Python 3.8+
- Africa's Talking developer account
- Google Cloud Project with Dialogflow CX agent
- Flask & pip

### 🔐 Environment Variables

Create a `.env` file in `backend/` with the following:

```
AT_USERNAME=your_at_username
AT_API_KEY=your_at_api_key
AT_SENDER_ID=optional_sender_id
ALERT_PHONE_NUMBER=admin_phone_number_to_alert

DIALOGFLOW_PROJECT_ID=your_project_id
DIALOGFLOW_LOCATION=your_agent_location
DIALOGFLOW_AGENT_ID=your_agent_id
DIALOGFLOW_LANGUAGE_CODE=en
GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json
```

---

## ⚙️ Installation

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ▶️ Running the Server

```bash
export FLASK_APP=app.py
flask run
```

The server will start at `http://127.0.0.1:5000`.

---

## 📡 Webhook Endpoint

### POST `/webhooks/incoming_sms`

Africa's Talking should send SMS data here.

#### Expected `application/x-www-form-urlencoded` data:

| Field | Description |
|-------|-------------|
| `from` | Sender phone number |
| `text` | Message content |

---

## 🧪 Testing Locally

You can simulate an incoming SMS by using `curl`:

```bash
curl -X POST http://127.0.0.1:5000/webhooks/incoming_sms \
     -d "from=+254712345678" \
     -d "text=report hazard broken ladder"
```

---

## 🧠 Dialogflow CX Integration

This backend will send incoming SMS to your Dialogflow CX agent using the `detect_intent_text()` function. Based on the agent's response and detected intent, it logs data in-memory and sends SMS confirmations or alerts.

### Example Intents (Dialogflow CX):
- `log_hazard`
- `log_attendance`
- `log_delivery`

---

```bash
ngrok http 5000
```

---

## 🧑‍💻 Contributors

- **@munyi** – Backend & Dialogflow integration
- Hackathon: [Africa's Talking ConTech Hackathon 2025](https://africastalking.com/)

---

## 📜 License

This project is released under the [MIT License](https://opensource.org/licenses/MIT).
