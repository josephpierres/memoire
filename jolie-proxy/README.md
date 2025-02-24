# Jolie Proxy Service

## Prérequis
- Jolie installé : [Guide d'installation](https://jolie-lang.org/)
- Accès à un environnement Docker avec des services MySQL et Redis configurés

## Structure du projet
- `jolie-proxy.ol` : Script principal
- `jolie-proxy-interface.iol` : Fichiers d'interface inclus

## Exécution
3. Création de l’Image Docker
4. Naviguez vers le répertoire contenant le fichier Dockerfile :

cd jolie-proxy

5. Construisez l'image Docker :

docker build -t your-dockerhub-username/jolie-proxy:latest .

docker run -p 9091:9091 jolie-proxy

6. Remplacez your-dockerhub-username par votre identifiant Docker Hub.



Configuration Prometheus
Ajoutez ce job à votre configuration Prometheus pour scraper les métriques :

yaml
Copy
scrape_configs:
  - job_name: 'kubescale_intelligence'
    static_configs:
      - targets: ['0.0.0.0:9091']
