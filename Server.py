import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")

def notify_line(access_token, user_id, message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    print("LINE API response:", response.status_code, response.text)  # ここを追加
    return response.status_code, response.text

@app.route('/send_message', methods=['POST'])
def send_message():
    req_data = request.get_json()
    user_id = req_data.get('user_id')
    message = req_data.get('message')
    if not user_id or not message:
        return jsonify({'error': 'user_id and message are required'}), 400
    status, resp = notify_line(ACCESS_TOKEN, user_id, message)
    return jsonify({'status': status, 'response': resp})

@app.route('/fall_detected', methods=['POST'])
def fall_detected():
    req_data = request.get_json()
    user_id = req_data.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    message = "転倒が検知されました！ご注意ください。"
    status, resp = notify_line(ACCESS_TOKEN, user_id, message)
    return jsonify({'status': status, 'response': resp})

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        event = request.get_json()['events'][0]
        user_id = event['source']['userId']
        reply_token = event['replyToken']
        reply_message = f"あなたのUser_IDは{user_id}です。"

        url = "https://api.line.me/v2/bot/message/reply"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "replyToken": reply_token,
            "messages": [
                {
                    "type": "text",
                    "text": reply_message
                }
            ]
        }
        response = requests.post(url, headers=headers, json=payload)
        print("LINE reply response:", response.status_code, response.text)
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        print("Webhook error:", e)
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)