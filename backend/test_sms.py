# File: test_sms.py

# Import necessary libraries
import os
from dotenv import load_dotenv
import africastalking

# Load environment variables from .env file located in the same directory
# This needs to be called BEFORE accessing environment variables with os.getenv
load_dotenv()

# --- Configuration ---
# Load credentials and settings from environment variables
at_username = os.getenv('AT_USERNAME')
at_api_key = os.getenv('AT_API_KEY')
test_recipient = os.getenv('ALERT_PHONE_NUMBER') # The phone number to send the test SMS to
at_sender_id = os.getenv('AT_SENDER_ID') # The Sender ID (Alphanumeric or Short Code) to use

# Define the message content
test_message = "This is a test message from ConstructAgent Standalone Script using a specific Sender ID."

# --- Print Configuration for Verification ---
print("--- Configuration Loaded ---")
print(f"Using Username: {at_username}")
# Mask the API key for security when printing
print(f"Using API Key: {'*' * len(at_api_key) if at_api_key else 'Not Set'}")
print(f"Attempting to send to: {test_recipient}")
# Clearly state which Sender ID will be used, or if it's the default
print(f"Using Sender ID: {at_sender_id if at_sender_id else 'Default (Not Set in .env)'}")
print("--------------------------")

# --- Validation Check ---
# Check if essential variables are loaded
if not all([at_username, at_api_key, test_recipient]):
    print("\nError: Ensure AT_USERNAME, AT_API_KEY, and ALERT_PHONE_NUMBER are set in your .env file.")
    # Optionally check for sender_id here if it's strictly required for the test:
    # elif not at_sender_id:
    #    print("\nError: AT_SENDER_ID is required for this test but not set in .env file.")

# --- Main Logic: Send SMS ---
# Proceed only if essential credentials are set
if all([at_username, at_api_key, test_recipient]):
    try:
        # --- Initialize SDK ---
        # Configure the SDK with your credentials
        print("\nInitializing Africa's Talking SDK...")
        africastalking.initialize(at_username, at_api_key)

        # Get the SMS service object
        sms = africastalking.SMS
        print("SDK Initialized.")

        # --- Send SMS ---
        print("\nAttempting to send SMS...")

        # Prepare arguments for the send call
        recipients_list = [test_recipient] # Must be a list

        # Call the sms.send method using the sender_id keyword argument if available
        if at_sender_id:
            # If AT_SENDER_ID was found in .env, use it
            response = sms.send(
                message=test_message,
                recipients=recipients_list,
                sender_id=at_sender_id # Use the specific sender ID
            )
        else:
            # If no sender_id is set in .env, call without the sender_id parameter
            # Africa's Talking will use the default associated with the API key
            # (often a shared shortcode in Sandbox, or requires configuration in Live)
            print("Warning: AT_SENDER_ID not set in .env. Sending with default Sender ID associated with the account.")
            response = sms.send(
                message=test_message,
                recipients=recipients_list
            )

        print("SMS send request completed.")

        # --- Print Response ---
        print("\n--- Africa's Talking API Response ---")
        print(response) # Print the full dictionary response from the API
        print("-------------------------------------")

    # --- Error Handling ---
    except Exception as e:
        # Catch any error during initialization or sending
        print(f"\n--- An Error Occurred ---")
        print(f"Error details: {e}")
        print("-------------------------")

else:
     # This else corresponds to the initial validation check failing
     print("\nSkipping SMS send due to missing essential configuration (Username, API Key, or Recipient).")


print("\nScript finished.")