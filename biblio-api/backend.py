import requests

# URL du proxy Jolie
RESERVE_BOOK_URL = "http://localhost:8080/reserveBook"
GET_BOOKS_URL = "http://localhost:8080/getBooks"

# Fonction pour réserver un livre
def reserve_book(event_id, user_id):
    reservation_data = {
        "eventId": event_id,
        "userId": user_id
    }
    try:
        response = requests.post(RESERVE_BOOK_URL, json=reservation_data)
        if response.status_code == 200:
            return response.json()  # Retourne la réponse du serveur
        else:
            return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}

# Fonction pour récupérer la liste des livres
def get_books():
    try:
        response = requests.get(GET_BOOKS_URL)
        if response.status_code == 200:
            return response.json()  # Retourne la liste des livres
        else:
            return {"error": response.text}
    except Exception as e:
        return {"error": str(e)}