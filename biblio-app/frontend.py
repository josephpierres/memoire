from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# URL du backend Flask
BACKEND_URL = "http://localhost:5000"

# Route pour la page d'accueil
@app.route('/')
def home():
    return render_template('index.html')

# Route pour réserver un book
@app.route('/reserve', methods=['POST'])
def reserve():
    event_id = request.form.get("eventId")
    user_id = request.form.get("userId")
    
    if not event_id or not user_id:
        return "eventId and userId are required", 400
    
    # Envoyer la requête de réservation au backend
    response = requests.post(f"{BACKEND_URL}/reserveBook", json={"eventId": event_id, "userId": user_id})
    
    if response.status_code == 200:
        return redirect(url_for('home'))  # Rediriger vers la page d'accueil après une réservation réussie
    else:
        return f"Failed to reserve book: {response.json().get('error', 'Unknown error')}", 400

# Route pour afficher la liste des books
@app.route('/books')
def books():
    # Récupérer la liste des books depuis le backend
    response = requests.get(f"{BACKEND_URL}/getBooks")
    
    if response.status_code == 200:
        books = response.json()
        return render_template('books.html', books=books)
    else:
        return f"Failed to retrieve books: {response.json().get('error', 'Unknown error')}", 400

# Démarrer le serveur Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)