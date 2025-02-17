from flask import Flask, render_template, request, redirect, url_for
import requests
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.exposition import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

# URL du backend Flask
BACKEND_URL = "http://biblio-api:5001"

# Prometheus Metrics
REQUEST_COUNT = Counter(
    "flask_frontend_requests_total", "Total number of requests", ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "flask_frontend_request_latency_seconds", "Request latency", ["method", "endpoint"]
)

# Route pour la page d'accueil
@app.route('/')
def home():
    start_time = time.time()
    REQUEST_COUNT.labels(method="GET", endpoint="/", http_status="200").inc()
    REQUEST_LATENCY.labels(method="GET", endpoint="/").observe(time.time() - start_time)
    return render_template('index.html')

# Route pour réserver un book
@app.route('/reserve', methods=['POST'])
def reserve():
    start_time = time.time()
    event_id = request.form.get("eventId")
    user_id = request.form.get("userId")
    
    if not event_id or not user_id:
        REQUEST_COUNT.labels(method="POST", endpoint="/reserve", http_status="400").inc()
        return "eventId and userId are required", 400
    
    # Envoyer la requête de réservation au backend
    response = requests.post(f"{BACKEND_URL}/reserveBook", json={"eventId": event_id, "userId": user_id})
    
    REQUEST_COUNT.labels(method="POST", endpoint="/reserve", http_status=str(response.status_code)).inc()
    REQUEST_LATENCY.labels(method="POST", endpoint="/reserve").observe(time.time() - start_time)

    if response.status_code == 200:
        return redirect(url_for('home'))  # Rediriger vers la page d'accueil après une réservation réussie
    else:
        return f"Failed to reserve book: {response.json().get('error', 'Unknown error')}", 400

# Route pour afficher la liste des books
@app.route('/books')
def books():
    start_time = time.time()
    response = requests.get(f"{BACKEND_URL}/getBooks")
    
    REQUEST_COUNT.labels(method="GET", endpoint="/books", http_status=str(response.status_code)).inc()
    REQUEST_LATENCY.labels(method="GET", endpoint="/books").observe(time.time() - start_time)

    if response.status_code == 200:
        books = response.json()
        return render_template('books.html', books=books)
    else:
        return f"Failed to retrieve books: {response.json().get('error', 'Unknown error')}", 400

# Endpoint pour exposer les métriques Prometheus
@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# Middleware pour Prometheus
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

# Démarrer le serveur Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
