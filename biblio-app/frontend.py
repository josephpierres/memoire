import requests
import time
import threading

# URL du backend
BACKEND_URL = "http://localhost:5000"

# Données de la réservation
reservation_data = {
    "eventId": "concert-123",
    "userId": "user-456"
}

# Fonction pour envoyer une requête POST (réserver un livre)
def reserve_book():
    while True:
        try:
            response = requests.post(f"{BACKEND_URL}/reserveBook", json=reservation_data)
            if response.status_code == 200:
                print("Reservation successful:", response.json())
            else:
                print("Error:", response.text)
        except Exception as e:
            print("Failed to send POST request:", e)
        
        # Attendre 5 secondes avant la prochaine requête
        time.sleep(5)

# Fonction pour envoyer une requête GET (récupérer la liste des livres)
def get_books():
    while True:
        try:
            response = requests.get(f"{BACKEND_URL}/getBooks")
            if response.status_code == 200:
                print("Books:", response.json())
            else:
                print("Error:", response.text)
        except Exception as e:
            print("Failed to send GET request:", e)
        
        # Attendre 20 secondes avant la prochaine requête
        time.sleep(20)

# Démarrer les threads pour les requêtes POST et GET
if __name__ == "__main__":
    # Thread pour les requêtes POST (réservation de livres)
    post_thread = threading.Thread(target=reserve_book)
    post_thread.daemon = True  # Le thread s'arrête lorsque le programme principal se termine

    # Thread pour les requêtes GET (récupération des livre)
    get_thread = threading.Thread(target=get_books)
    get_thread.daemon = True  # Le thread s'arrête lorsque le programme principal se termine

    # Démarrer les threads
    post_thread.start()
    get_thread.start()

    # Maintenir le programme en cours d'exécution
    try:
        while True:
            time.sleep(1)  # Maintenir le programme actif
    except KeyboardInterrupt:
        print("Program stopped.")