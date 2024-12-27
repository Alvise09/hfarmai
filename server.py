from flask import Flask, request, jsonify
from langchain_experimental.agents import create_csv_agent
from langchain_openai import ChatOpenAI
from flask_cors import CORS
import os
import requests  # Per scaricare il file CSV

app = Flask(__name__)
CORS(app)

api_key = os.getenv('OPENAI_API_KEY')

agent = None  # Inizializza agent come None


@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    global agent
    csv_url = request.json.get('csv_url')
    
    if not csv_url:
        return jsonify({"response": "No CSV URL provided."}), 400

    try:
        # Scarica il file CSV
        response = requests.get(csv_url)
        if response.status_code == 200:
            with open('dataset.csv', 'wb') as f:
                f.write(response.content)  # Salva il file come 'dataset.csv'
            print("[INFO] CSV file downloaded successfully.")
        else:
            raise Exception(f"Failed to download CSV file. Status code: {response.status_code}")

        # Inizializza l'agente con il nuovo CSV
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        agent = create_csv_agent(llm, 'dataset.csv', verbose=True, allow_dangerous_code=True)
        print("[INFO] Agent initialized successfully.")
        return jsonify({"response": "CSV file uploaded and agent initialized successfully."}), 200
    except Exception as e:
        print(f"[ERROR] Failed to process CSV URL: {e}")
        return jsonify({"response": f"Failed to process CSV URL: {e}"}), 500


@app.route('/get_response', methods=['POST', 'OPTIONS'])
def get_response():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    if agent is None:
        return jsonify({"response": "Agent not initialized. Upload a CSV file first."}), 400

    user_message = request.json.get('message')
    print(f"[DEBUG] Received message: {user_message}")

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
