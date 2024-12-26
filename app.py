from flask import Flask, request, jsonify
from langchain_experimental.agents import create_csv_agent
from langchain_openai import ChatOpenAI  # Correct updated import
from flask_cors import CORS  # Import flask_cors to handle CORS issues
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

api_key = os.getenv('OPENAI_API_KEY')

try:
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)  # Load the updated model
    agent = create_csv_agent(llm, 'dataset.csv', verbose=True, allow_dangerous_code=True)
except Exception as e:
    print(f"Failed to initialize agent: {e}")

@app.route('/get_response', methods=['POST', 'OPTIONS'])
def get_response():
    if request.method == 'OPTIONS':
        # Handle preflight requests automatically
        return jsonify({}), 200

    user_message = request.json.get('message')
    print(f"[DEBUG] Received message: {user_message}")  # Log user input for debugging

    if not user_message:
        print("[DEBUG] Empty user message received.")
        return jsonify({"response": "Please ask a valid question."})

    try:
        print("[DEBUG] Sending request to agent...")
        response = agent.run(user_message)
        print(f"[DEBUG] Response from agent: {response}")
        return jsonify({"response": response})
    except Exception as e:
        print(f"[ERROR] Exception in agent response: {e}")
        return jsonify({"response": "Failed to process the request."})


if __name__ == '__main__':
    app.run(debug=True)
