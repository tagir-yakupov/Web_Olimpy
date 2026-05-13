from flask import Blueprint, jsonify, request
import requests

api_key = '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'

chatt = Blueprint('chat', __name__, url_prefix='/')

@chatt.route('/chat', methods=['POST'])
def chat_ai():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/free",
                "messages": [
                    {
                        "role": "user",
                        "content": f"{user_message}"
                    }
                ]
            }
        )
        if response.status_code == 200:
            result = response.json()
            reply = result['choices'][0]['message']['content']
            return jsonify({'reply': reply})
        else:
            return jsonify({'reply': f'Ошибка {response.status_code}: {response.text}'})
    
    except Exception as e:
        print(f"Исключение: {e}")
        return jsonify({'reply': f'Ошибка: {str(e)}'})