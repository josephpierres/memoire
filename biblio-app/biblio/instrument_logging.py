import logging
from fluent import handler
from datetime import datetime

def LogsInstrumentor(service_name, fluent_endpoint="24224"):
    custom_format = {
        "Label": "%(name)s",
        "PId": "%(process)d",
        "Date": "%(asctime)s",
        "Node": "R30-M0-N9-C:J16-U01",  # Exemple statique, remplacez par une valeur dynamique si nécessaire
        "Timestamp": "%(created)f",
        "Type": "APP-KERNEL",
        "Component": service_name,
        "Level": "%(levelname)s",
        "Content": "%(message)s",
    }

    logging.basicConfig(level=logging.INFO, format="%(message)s")   
    h = handler.FluentHandler(service_name, host='host', port=fluent_endpoint)
    formatter = handler.FluentRecordFormatter(custom_format)
    h.setFormatter(formatter)
    return  h

# Formatter personnalisé
class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Champs personnalisés
        label = record.name
        pid = record.process
        date = datetime.now().strftime("%Y.%m.%d")
        node = "R30-M0-N9-C:J16-U01BIBLIO-APP"  # Identifiant de nœud statique ou dynamique
        timestamp = datetime.now().strftime("%Y-%m-%d-%H.%M.%S.%f")[:-3]  # Timestamp avec millisecondes
        log_type = "KERNEL"  # Type défini statiquement
        component = record.name  # Nom du service
        level = record.levelname
        content = record.getMessage()

        # Assemblage du message formaté
        return f"{label} {pid} {date} {node} {timestamp} {log_type} {component} {level} {content}"
    
# Configuration du logger
def configure_logger(service_name):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    # Handler avec sortie sur la console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())

    # Ajout du handler au logger
    logger.addHandler(console_handler)
    return logger
