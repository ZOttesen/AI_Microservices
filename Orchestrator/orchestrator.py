from flask import Flask, request, jsonify
import requests
import pybreaker

app = Flask(__name__)

# Setup Circuit Breaker for OpenAI service
openai_circuit_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30)

# Fallback function in case of OpenAI failure
def openai_fallback(text):
    return "Fallback response: Unable to process your request at this time."

@app.route('/process-text', methods=['POST'])
def process_text():
    input_text = request.json.get('text')

    # Step 1: Call OpenAI service
    try:
        ai_response = openai_circuit_breaker.call(lambda: requests.post('http://openai-service:5002/generate', json={'text': input_text}))
        ai_text = ai_response.json().get('response')
    except pybreaker.CircuitBreakerError:
        ai_text = openai_fallback(input_text)

    # Step 2: Optionally call Text-to-Speech service if needed
    # Here we just return the ai_text as the response
    return jsonify({'text': ai_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)