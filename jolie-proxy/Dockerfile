# Utiliser l'image de base officielle Jolie
FROM jolielang/jolie:latest

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires dans l'image
COPY main.ol /app/
COPY proxyInterface.iol /app/
# Copier les fichiers nécessaires dans l'image


# Variables d'environnement par défaut (à surcharger via Helm / K8s)
ENV ALERTMANAGER_HOST=alertmanager.monitoring.svc.cluster.local
ENV ALERTMANAGER_PORT=9093
ENV REDIS_HOST=redis.bbl
ENV REDIS_PORT=6379
ENV MYSQL_HOST=mysql.bbl
ENV MYSQL_PORT=3306
ENV KEDA_HOST=keda-operator.keda
ENV KEDA_PORT=8084
ENV PROMETHEUS_HOST=prometheus.monitoring.svc.cluster.local
ENV PROMETHEUS_PORT=9090

# Expose le port 8090 pour le service biblio-api
EXPOSE 8090 
# Expose le port 9091 pour les metriques
EXPOSE 9091

# Commande pour démarrer le service Jolie
CMD ["jolie", "main.ol"]
