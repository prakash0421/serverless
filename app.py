# app.py
from flask import Flask, request, jsonify
import boto3

app = Flask(__name__)

# Initialize AWS SES client
ses_client = boto3.client('ses', region_name='us-east-1')

@app.route('/send', methods=['POST'])
def send_email():
    try:
        data = request.json
        receiver_email = data.get('receiver_email')
        subject = data.get('subject')
        body_text = data.get('body_text')

        if not all([receiver_email, subject, body_text]):
            return jsonify({"error": "Missing required parameters"}), 400

        response = ses_client.send_email(
            Source='iamprakash2104@gmail.com',  # Replace with a verified sender email
            Destination={
                'ToAddresses': [receiver_email]
            },
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body_text}}
            }
        )

        return jsonify({"message": "Email sent successfully", "message_id": response['MessageId']}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
