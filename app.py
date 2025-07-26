from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from chatbot import GovernmentChatbot
import os

app = Flask(__name__)
CORS(app)

# Initialize chatbot
chatbot = GovernmentChatbot()
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HKTS Government Chatbot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 80vh;
            background: white;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
        }
        
        .chat-header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 20px;
            max-width: 70%;
        }
        
        .user-message {
            background: #007bff;
            color: white;
            margin-left: auto;
        }
        
        .bot-message {
            background: #e9ecef;
            color: #333;
        }
        
        .chat-input {
            display: flex;
            padding: 20px;
            background: white;
            border-radius: 0 0 10px 10px;
        }
        
        #messageInput {
            flex: 1;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 25px;
            outline: none;
            font-size: 16px;
        }
        
        #sendButton {
            margin-left: 10px;
            padding: 15px 25px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
        }
        
        #sendButton:hover {
            background: #0056b3;
        }
        
        .language-toggle {
            margin: 10px 0;
            text-align: center;
        }
        
        .lang-btn {
            margin: 0 10px;
            padding: 8px 16px;
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
        }
        
        .lang-btn.active {
            background: #28a745;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h2>HKTS Government Website Assistant</h2>
            <p>Ask me anything about government services and information</p>
            <div class="language-toggle">
                <button class="lang-btn active" onclick="setLanguage('english')">English</button>
                <button class="lang-btn" onclick="setLanguage('hindi')">हिंदी</button>
            </div>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                Hello! I'm your government website assistant. How can I help you today?
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" id="messageInput" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
            <button id="sendButton" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let currentLanguage = 'english';
        
        function setLanguage(lang) {
            currentLanguage = lang;
            document.querySelectorAll('.lang-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            const placeholder = lang === 'hindi' ? 'यहाँ अपना संदेश लिखें...' : 'Type your message here...';
            document.getElementById('messageInput').placeholder = placeholder;
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            addMessage(message, 'user');
            input.value = '';
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        language: currentLanguage
                    })
                });
                
                const data = await response.json();
                addMessage(data.response, 'bot');
                
            } catch (error) {
                addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
        }
        
        function addMessage(message, sender) {
            const messagesDiv = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = message;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        language = data.get('language', 'english')
        
        response = chatbot.get_response(message, language)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'response': 'Sorry, I encountered an error processing your request.',
            'status': 'error',
            'error': str(e)
        })

@app.route('/api/train', methods=['POST'])
def train():
    """API endpoint to retrain the chatbot with new data"""
    try:
        chatbot.load_and_process_data()
        return jsonify({
            'message': 'Chatbot retrained successfully',
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'message': 'Error retraining chatbot',
            'status': 'error',
            'error': str(e)
        })

if __name__ == '__main__':
    print("Starting Government Chatbot Server...")
    print("Access the chatbot at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)