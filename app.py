from flask import Flask, request
import requests, os

app = Flask(__name__)
TOKEN = os.environ.get("ACCESS_TOKEN", "")
VERIFY = os.environ.get("VERIFY_TOKEN", "")
IG_ID = os.environ.get("IG_ID", "")
API = "https://graph.facebook.com/v21.0"

KEYWORD = "link"
PUBLIC_REPLY = "DM check karo! 🔥"
DM_TEXT = "Ye raha link: https://your-link.com"
STORY_REPLY = "Thanks! Details ke liye humara link: https://your-link.com"

def send_dm(recipient, text):
    requests.post(f"{API}/{IG_ID}/messages",
        params={"access_token": TOKEN},
        json={"recipient": recipient, "message": {"text": text}})

@app.get("/")
def home():
    return "Bot chal raha hai"

@app.get("/webhook")
def verify():
    if request.args.get("hub.verify_token") == VERIFY:
        return request.args.get("hub.challenge", "")
    return "forbidden", 403

@app.post("/webhook")
def webhook():
    data = request.json or {}
    for entry in data.get("entry", []):
        for ch in entry.get("changes", []):
            if ch.get("field") != "comments":
                continue
            v = ch["value"]
            if v["from"]["id"] == IG_ID:
                continue
            if KEYWORD in v.get("text", "").lower():
                cid = v["id"]
                requests.post(f"{API}/{cid}/replies",
                    params={"access_token": TOKEN},
                    data={"message": PUBLIC_REPLY})
                send_dm({"comment_id": cid}, DM_TEXT)
        for m in entry.get("messaging", []):
            msg = m.get("message", {})
            if m["sender"]["id"] == IG_ID or msg.get("is_echo"):
                continue
            if "reply_to" in msg and "story" in msg["reply_to"]:
                send_dm({"id": m["sender"]["id"]}, STORY_REPLY)
    return "ok", 200
