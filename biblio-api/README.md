# Pour tester
## Dans les environnements Linux, il est nécessaire d'installer les bibliothèques libmatthew afin de permettre la communication entre jocker et Docker sur les sockets unix locaux. Dans Ubuntu, il est nécessaire de :

sudo apt update
sudo apt install libunixsocket-java
cp /usr/lib/jni/libunix-java.so /usr/lib64/libmatthew-java/libunix-java.so

Instaler l'environement de python
sudo apt install python3-venv

# Maintenant, exécutez la commande suivante pour créer l’environnement virtuel :
python3 -m venv .venv

# Pour activer un environnement virtuel, entrez cette commande :
source .venv/bin/activate

# Si vous devez désactiver un environnement virtuel, exécutez simplement la commande suivante :
deactivate
rm -rf monenv

# installer les bibliotheques
apt-get update
pip install --upgrade pip

# installer les dependances à Python
pip install -r requirements.txt 

# donc pour chacun des projets
pip install -r biblio-app/requirements.txt 
pip install -r biblio-api/requirements.txt 