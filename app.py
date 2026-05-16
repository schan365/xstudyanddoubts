from flask import Flask, request
import requests
import os

app = Flask(__name__)

VERIFY_TOKEN = "my_verify_token"

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

CONVERSATION_FOLDER = "conversations"


# HOME PAGE
@app.route("/", methods=["GET"])
def home():
    return "Malayalam Facebook Bot Running"


# FACEBOOK WEBHOOK VERIFICATION
@app.route("/webhook", methods=["GET"])
def verify():

    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge

    return "Verification failed"


# FACEBOOK MESSAGE RECEIVER
@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json

    for entry in data.get("entry", []):

        for messaging in entry.get("messaging", []):

            sender_id = messaging["sender"]["id"]

            if messaging.get("message"):

                user_message = messaging["message"].get("text", "")

                if not user_message:
                    continue

                reply = get_reply(user_message)

                send_message(sender_id, reply)

    return "ok", 200


# SEARCH REPLY FROM FILES
def get_reply(user_text):

    user_text = user_text.lower()

    for filename in os.listdir(CONVERSATION_FOLDER):

        filepath = os.path.join(CONVERSATION_FOLDER, filename)

        if not filename.endswith(".txt"):
            continue

        with open(filepath, "r", encoding="utf-8") as f:

            for line in f:

                line = line.strip()

                if "=" not in line:
                    continue

                keyword, reply = line.split("=", 1)

                keyword = keyword.lower().strip()

                if keyword in user_text:
                    return reply.strip()

    return "ക്ഷമിക്കണം 😊 എനിക്ക് മനസ്സിലായില്ല."


# SEND MESSAGE TO FACEBOOK
def send_message(user_id, text):

    url = f"https://graph.facebook.com/v19.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"

    payload = {
        "recipient": {"id": user_id},
        "message": {"text": text}
    }

    requests.post(url, json=payload)


# START APP
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
