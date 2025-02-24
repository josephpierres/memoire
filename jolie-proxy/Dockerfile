# Utiliser l'image de base officielle Jolie
FROM jolielang/jolie:latest

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires dans l'image
COPY jolie-proxy-interface.iol /app/
COPY jolie-proxy.ol /app/
COPY /lib /app/lib
# Expose le port 9091 
EXPOSE 9091
# Commande pour démarrer le service Jolie
CMD ["jolie", "jolie-proxy.ol"]
