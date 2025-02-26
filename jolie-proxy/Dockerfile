# Utiliser l'image de base officielle Jolie
FROM jolielang/jolie:latest

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

ENV MYSQL_HOST=mysql
ENV MYSQL_PORT=3306
ENV MYSQL_USER=root
ENV MYSQL_PASSWORD=password
ENV MYSQL_DB=gestion_bibliotheque

# Copier les fichiers nécessaires dans l'image
COPY jolie-proxy-interface.iol /app/
COPY jolie-proxy.ol /app/
COPY /lib /app/lib
# Expose le port 9091 pour le service Jolie
EXPOSE 9091
# Port pour le service des metrics qui supporte uniquement le protocole http en format = plain
EXPOSE 9092     
# Commande pour démarrer le service Jolie
CMD ["jolie", "jolie-proxy.ol"]
