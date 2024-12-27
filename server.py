from flask import Flask, request, jsonify
from langchain_experimental.agents import create_csv_agent
from langchain_openai import ChatOpenAI
from flask_cors import CORS
import os
import requests
import asyncio

app = Flask(__name__)
CORS(app)

# Imposta la chiave API per OpenAI (o puoi prenderla dal tuo ambiente)
os.environ["OPENAI_API_KEY"] = "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"

# Funzione asincrona per scaricare il CSV da un URL
async def download_csv(csv_url):
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, requests.get, csv_url)
    
    if response.status_code == 200:
        with open('dataset.csv', 'wb') as f:
            f.write(response.content)
        return True
    return False

# Funzione per inizializzare il modello e l'agent
async def initialize_agent(csv_url):
    # Scarica il CSV
    if await download_csv(csv_url):
        # Inizializza l'agent con il file CSV scaricato
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        agent = create_csv_agent(llm, 'dataset.csv', verbose=True, allow_dangerous_code=True)
        return agent
    return None

@app.route('/get_response', methods=['POST', 'OPTIONS'])
async def get_response():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    user_message = request.json.get('message')
    csv_url = request.json.get('csv_url')

    if not user_message:
        return jsonify({"response": "Please ask a valid question."})

    if not csv_url:
        return jsonify({"response": "Please provide a valid CSV URL."})

    try:
        # Inizializza l'agent con il link del CSV fornito
        agent = await initialize_agent(csv_url)

        if agent is None:
            return jsonify({"response": "Failed to download or process CSV."})

        # Ottieni la risposta dal bot
        response = agent.run(user_message)
        return jsonify({"response": response})
    except Exception as e:
        print(f"[ERROR] Exception in agent response: {e}")
        return jsonify({"response": "Failed to process the request."})


if __name__ == '__main__':
    app.run(debug=True)
