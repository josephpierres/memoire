from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# URL du proxy Jolie
RESERVE_TICKET_URL = "http://localhost:8080/reserveTicket"
GET_TICKETS_URL = "http://localhost:8080/getTickets"

# Endpoint pour réserver un ticket
@app.route('/reserveTicket', methods=['POST'])
def reserve_ticket():
    data = request.json
    event_id = data.get("eventId")
    user_id = data.get("userId")
    
    if not event_id or not user_id:
        return jsonify({"error": "eventId and userId are required"}), 400
    
    try:
        response = requests.post(RESERVE_TICKET_URL, json={"eventId": event_id, "userId": user_id})
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint pour récupérer la liste des tickets
@app.route('/getTickets', methods=['GET'])
def get_tickets():
    try:
        response = requests.get(GET_TICKETS_URL)
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({"error": response.text}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Démarrer le serveur Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)