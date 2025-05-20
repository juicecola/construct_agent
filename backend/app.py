# File: app.py (Reverted to a simpler version)
# Description: Basic Flask backend for ConstructAgent. Handles AT webhooks,
# calls Dialogflow, performs basic fulfillment (logging, SMS alerts), provides API.

import os
import uuid
import json # Still useful for debugging parameters

from flask import Flask, request, jsonify, make_response
from dotenv import load_dotenv
import africastalking

# --- Attempt to import Dialogflow CX libraries ---
try:
    from google.cloud.dialogflowcx_v3beta1.services.sessions import SessionsClient
    from google.cloud.dialogflowcx_v3beta1.types import session as types_session
    dialogflow_imported = True
except ImportError:
    print("WARNING: google-cloud-dialogflow-cx library not found.")
    dialogflow_imported = False
    SessionsClient = None
    types_session = None

# --- Load Environment Variables ---
load_dotenv()
print("Loading environment variables...")

# --- Initialization ---
app = Flask(__name__)

# --- Africa's Talking Configuration & Initialization ---
at_username = os.getenv('AT_USERNAME')
at_api_key = os.getenv('AT_API_KEY')
at_sender_id = os.getenv('AT_SENDER_ID') # Load Sender ID
alert_phone = os.getenv('ALERT_PHONE_NUMBER')

# Initialize AT SDK globally
at_sms = None
try:
    if at_username and at_api_key:
        africastalking.initialize(at_username, at_api_key)
        at_sms = africastalking.SMS
        print("Africa's Talking SDK Initialized.")
    else:
        print("WARNING: AT Username or API Key missing. AT SDK not initialized.")
except Exception as e:
    print(f"ERROR: Failed to initialize Africa's Talking SDK: {e}")

# --- Dialogflow CX Configuration & Initialization ---
dialogflow_client = None
dialogflow_project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
dialogflow_location = os.getenv('DIALOGFLOW_LOCATION')
dialogflow_agent_id = os.getenv('DIALOGFLOW_AGENT_ID')
dialogflow_language_code = os.getenv('DIALOGFLOW_LANGUAGE_CODE', 'en')
google_creds_path_env = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if dialogflow_imported and all([dialogflow_project_id, dialogflow_location, dialogflow_agent_id, google_creds_path_env]):
    if os.path.exists(google_creds_path_env):
        try:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_creds_path_env
            client_options = None
            if dialogflow_location != 'global':
                client_options = {"api_endpoint": f"{dialogflow_location}-dialogflow.googleapis.com"}
            dialogflow_client = SessionsClient(client_options=client_options)
            print("Dialogflow CX Client Initialized.")
        except Exception as e:
            print(f"ERROR: Failed to initialize Dialogflow CX Client: {e}")
    else:
        print(f"ERROR: Google credentials file not found at path: {google_creds_path_env}")
else:
    print("Skipping Dialogflow CX Client initialization due to missing config or library.")


# --- In-Memory Data Stores (Simple Lists) ---
hazard_logs = []
attendance_logs = []
delivery_logs = []

# --- Helper Function for Dialogflow ---
def detect_intent_text(session_id: str, text: str):
    """Sends text to Dialogflow CX API."""
    if not dialogflow_client:
        print("ERROR: Dialogflow client not available.")
        return None

    session_path = f"projects/{dialogflow_project_id}/locations/{dialogflow_location}/agents/{dialogflow_agent_id}/sessions/{session_id}"
    text_input = types_session.TextInput(text=text)
    query_input = types_session.QueryInput(text=text_input, language_code=dialogflow_language_code)
    request_dialogflow = types_session.DetectIntentRequest(session=session_path, query_input=query_input)

    print(f"Sending to Dialogflow: Session={session_id}, Text='{text}'") # Keep basic log
    try:
        response = dialogflow_client.detect_intent(request=request_dialogflow)
        print("Dialogflow Response Received.")
        return response.query_result
    except Exception as e:
        print(f"ERROR: Dialogflow detectIntent call failed: {e}")
        return None

# --- Webhook Endpoints ---

@app.route('/webhooks/incoming_sms', methods=['POST'])
def incoming_sms():
    """Handles incoming SMS from Africa's Talking."""
    data = request.form
    sender = data.get('from')
    text = data.get('text')
    print(f"--- Incoming SMS From: {sender}, Text: '{text}' ---")

    if not sender or text is None:
        return "Missing required fields", 200 # Still return 200 OK

    session_id = f"sms_{sender.replace('+', '')}"
    detect_intent_text(session_id, text) # Call Dialogflow

    return "SMS Received", 200 # Acknowledge receipt

@app.route('/webhooks/incoming_ussd', methods=['POST'])
def incoming_ussd():
    """Handles incoming USSD requests from Africa's Talking."""
    data = request.form
    session_id_ussd = data.get('sessionId')
    phone_number = data.get('phoneNumber')
    text = data.get('text', '')
    print(f"--- Incoming USSD From: {phone_number}, Session: {session_id_ussd}, Input: '{text}' ---")

    if not session_id_ussd or not phone_number:
         response_text = "END Service error. Please try again."
         response = make_response(response_text, 200)
         response.headers['Content-Type'] = 'text/plain'
         return response

    df_session_id = f"ussd_{phone_number.replace('+', '')}_{session_id_ussd}"
    query_result = detect_intent_text(df_session_id, text)

    # Simplified USSD Response Logic
    response_text = "Sorry, an error occurred." # Default error
    response_prefix = "END" # Default to end on error or no message

    if query_result:
        messages = [msg.text.text[0] for msg in query_result.response_messages if hasattr(msg, 'text') and msg.text.text]
        if messages:
            response_text = "\n".join(messages)
            # Basic check for ending interaction based on intent flag
            if not (query_result.match and query_result.match.intent and query_result.match.intent.end_interaction):
                 response_prefix = "CON" # Continue if not explicitly ended
            else:
                 response_prefix = "END"
        else:
            # If no message, assume END unless fulfillment logic implies otherwise (not handled here)
            response_text = "Thank you."
            response_prefix = "END"

    final_response = f"{response_prefix} {response_text}"
    print(f"USSD Response: {final_response}")
    response = make_response(final_response, 200)
    response.headers['Content-Type'] = 'text/plain'
    return response


# In app.py

@app.route('/webhooks/fulfillment', methods=['POST'])
def fulfillment():
    req = request.get_json(force=True) # Get the JSON payload from Dialogflow

    # Extract useful information from the request
    intent_name = req.get('intentInfo', {}).get('displayName', 'Unknown Intent')
    params = req.get('sessionInfo', {}).get('parameters', {})
    tag = req.get('fulfillmentInfo', {}).get('tag', '') # Get the tag you set

    print(f"--- Fulfillment Request Received ---")
    print(f"Tag: {tag}")
    print(f"Intent: {intent_name}")
    print(f"Parameters: {params}")

    # --- Initialize response payload for Dialogflow ---
    # Dialogflow expects a JSON response back. Even if you don't send a message
    # back *through* Dialogflow, you need to return this structure.
    response_payload = {
        "fulfillment_response": {
            "messages": []
            # You could add messages here if you want Dialogflow to say something
            # AFTER the fulfillment is complete. Example:
            # "messages": [{
            #     "text": {
            #         "text": ["Okay, I've logged the hazard and sent an alert."]
            #     }
            # }]
        }
        # You can also merge behavior with session parameters if needed
        # "sessionInfo": {
        #     "parameters": { ... updated parameters ... }
        # }
    }

    # --- Action Logic based on Tag or Intent ---
    try:
        # Using the tag is often cleaner if one endpoint handles multiple actions
        if tag == 'log_hazard_alert':
            location = params.get('site_location', 'Unknown Location')
            description = params.get('hazard_description', 'No description')
            # NOTE: Getting the original reporter's phone number here requires
            # more advanced setup (passing it via session parameters from the start).
            # For now, we'll use a placeholder.
            sender_info = "Reported via System"

            log_entry = {"timestamp": "NOW_FULFILL", "location": location, "description": description, "reporter": sender_info}
            hazard_logs.append(log_entry) # Assumes hazard_logs is accessible here
            print(f"Hazard Logged via Fulfillment: {log_entry}")

            # Send alert using Africa's Talking SMS API
            alert_msg = f"ALERT (via Fulfillment): Hazard '{description}' reported near '{location}'."
            # Ensure alert_phone and at_sms are accessible
            at_sms.send(alert_msg, [alert_phone])
            print(f"Alert SMS sent via Fulfillment to {alert_phone}")

            # Optional: Add a success message to the response Dialogflow sends
            response_payload["fulfillment_response"]["messages"].append({
                 "text": {"text": ["Hazard logged and alert sent."]}
            })

        elif tag == 'log_check_in' or tag == 'log_check_out': # Example for attendance
             worker_id = params.get('worker_id', 'Unknown Worker')
             action = "Check-In" if tag == 'log_check_in' else "Check-Out"
             log_entry = {"timestamp": "NOW_FULFILL", "worker_id": worker_id, "action": action}
             attendance_logs.append(log_entry)
             print(f"Attendance Logged via Fulfillment: {log_entry}")
             # Add appropriate message to response_payload if needed

        elif tag == 'log_delivery': # Example for delivery
             order_id = params.get('order_id', 'Unknown Order')
             location = params.get('site_location', 'Unknown Site')
             log_entry = {"timestamp": "NOW_FULFILL", "order_id": order_id, "location": location}
             delivery_logs.append(log_entry)
             print(f"Delivery Logged via Fulfillment: {log_entry}")
             # Send notification SMS via AT
             notify_msg = f"DELIVERY (via Fulfillment): Order '{order_id}' at '{location}' logged."
             at_sms.send(notify_msg, [alert_phone])
             print(f"Delivery Notification sent via Fulfillment to {alert_phone}")
             # Add appropriate message to response_payload if needed

        else:
            print(f"Warning: Unhandled fulfillment tag '{tag}' or intent '{intent_name}'")
            # Optionally add a generic error message to the response payload

    except Exception as e:
        print(f"ERROR during fulfillment processing: {e}")
        # Optionally add an error message for Dialogflow to relay
        response_payload["fulfillment_response"]["messages"] = [{
            "text": {"text": ["Sorry, there was an error processing your request via fulfillment."]}
        }]

    # --- Return the JSON response to Dialogflow ---
    print(f"--- Sending Fulfillment Response to Dialogflow ---")
    print(f"{response_payload}")
    return jsonify(response_payload)

# --- API Endpoints for Frontend Dashboard ---

@app.route('/api/hazards', methods=['GET'])
def get_hazards():
    """Provides hazard log data."""
    print("API Request: /api/hazards")
    return jsonify(hazard_logs if isinstance(hazard_logs, list) else [])

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    """Provides attendance log data."""
    print("API Request: /api/attendance")
    return jsonify(attendance_logs if isinstance(attendance_logs, list) else [])

@app.route('/api/deliveries', methods=['GET'])
def get_deliveries():
    """Provides delivery log data."""
    print("API Request: /api/deliveries")
    return jsonify(delivery_logs if isinstance(delivery_logs, list) else [])


# --- Run Flask App ---
if __name__ == '__main__':
    print("Starting Flask development server...")
    app.run(host='0.0.0.0', port=5000, debug=True)