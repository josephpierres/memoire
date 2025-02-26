// ✅ Interface pour la gestion des réservations et des livres
interface ProxyInterface {
    RequestResponse:        
        executeQuery(SqlRequest)(SqlResponse),
        metrics(void)(undefined),
        alert(undefined)(void)
}

interface MetricsInterface {
    RequestResponse:      
        metrics(void)(undefined)        
}

// 📌 Définition des types de données

// Type de données pour les requêtes SQL entrantes
type SqlRequest {
    query: string
}
// Type de données pour les réponses SQL
type SqlResponse {
    result?: undefined
    error?: string
    status: string
}

type AlertRequest {
    status: string
    labels: undefined
    annotations: undefined
}

type MetricsResponse {
    metrics: string
}