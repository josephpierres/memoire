// Port d'entrée pour l'application Python
inputPort PythonPort {
    Location: "socket://0.0.0.0:8080"
    Protocol: http {
        format = "json"
    }
    Interfaces: PythonInterface
}

// Port de sortie pour MySQL
outputPort MySQLPort {
    Location: "socket://mysql:3306"
    Protocol: http {
        format = "json"
    }
    Interfaces: MySQLInterface
}

// Port de sortie pour Redis
outputPort RedisPort {
    Location: "socket://redis:6379"
    Protocol: http {
        format = "json"
    }
    Interfaces: RedisInterface
}

// Port de sortie pour Prometheus
outputPort PrometheusAPI {
    Location: "socket://prometheus:9090"
    Protocol: http {
        format = "json"
    }
    Interfaces: PrometheusInterface
}
