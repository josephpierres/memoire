// ✅ Interface pour la gestion des réservations et des livres
interface ProxyInterface {
    RequestResponse:
        reserveBook(BookRequest)(BookResponse),
        getBooks(void)(undefined),
        metrics(void)(MetricsResponse)
}

// ✅ Interface pour la gestion des alertes
interface AlertInterface {
    RequestResponse:
        alert(undefined)(void)
}

// 📌 Définition des types de données
type BookRequest {
    eventId: string
    userId: string
}

type BookResponse {
    bookId?: string
    status: string
    error?: string
}

type BookListResponse {
    books: undefined
}

type AlertRequest {
    status: string
    labels: undefined
    annotations: undefined
}

type MetricsResponse {
    metrics: string
}