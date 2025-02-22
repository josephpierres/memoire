from flask import Flask, request, jsonify
import requests
import time
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
from prometheus_client import CONTENT_TYPE_LATEST
from prometheus_client.exposition import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

# URL du proxy Jolie
RESERVE_BOOK_URL = "http://jolie-proxy:9091/reserveBook"
GET_BOOKS_URL = "http://jolie-proxy:9091/getBooks"

# Prometheus Metrics
REQUEST_COUNT = Counter(
    "flask_requests_total", "Total number of requests", ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "flask_request_latency_seconds", "Request latency", ["method", "endpoint"]
)

# Endpoint pour réserver un book
@app.route('/reserveBook', methods=['POST'])
def reserve_book():
    start_time = time.time()
    data = request.json
    event_id = data.get("eventId")
    user_id = data.get("userId")

    if not event_id or not user_id:
        REQUEST_COUNT.labels(method="POST", endpoint="/reserveBook", http_status="400").inc()
        return jsonify({"error": "eventId and userId are required"}), 400
    
    try:
        response = requests.post(RESERVE_BOOK_URL, json={"eventId": event_id, "userId": user_id})
        REQUEST_COUNT.labels(method="POST", endpoint="/reserveBook", http_status=str(response.status_code)).inc()
        REQUEST_LATENCY.labels(method="POST", endpoint="/reserveBook").observe(time.time() - start_time)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        REQUEST_COUNT.labels(method="POST", endpoint="/reserveBook", http_status="500").inc()
        return jsonify({"error": str(e)}), 500

# Endpoint pour récupérer la liste des books
@app.route('/getBooks', methods=['GET'])
def get_books():
    start_time = time.time()
    try:
        response = requests.get(GET_BOOKS_URL)
        REQUEST_COUNT.labels(method="GET", endpoint="/getBooks", http_status=str(response.status_code)).inc()
        REQUEST_LATENCY.labels(method="GET", endpoint="/getBooks").observe(time.time() - start_time)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        REQUEST_COUNT.labels(method="GET", endpoint="/getBooks", http_status="500").inc()
        return jsonify({"error": str(e)}), 500

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
    app.run(host="0.0.0.0", port=5001)
