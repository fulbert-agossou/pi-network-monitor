# Station de monitoring réseau — Raspberry Pi 4

Projet personnel — Génie électrique, concentration génie informatique

Une station de surveillance réseau qui tourne sur un Raspberry Pi 4, détecte
les appareils connectés à un réseau local, signale les appareils inconnus ou
les comportements suspects, et affiche le tout dans un dashboard web.

## Fonctionnalités

- Découverte des appareils du réseau via des requêtes ARP (librairie Scapy)
- Détection de nouveaux appareils non reconnus
- Détection d'usurpation ARP (une IP connue soudainement associée à une
  nouvelle adresse MAC)
- Journalisation de tous les événements dans une base SQLite
- Dashboard web (Flask) avec liste des appareils et journal d'événements
- Approbation manuelle des appareils connus depuis l'interface

## Architecture

Le projet est divisé en modules indépendants :

- `scanner.py` : scanne le réseau via Scapy et retourne la liste des
  appareils actifs (IP, MAC, hostname)
- `detector.py` : compare le résultat du scan à la base de données pour
  détecter les nouveautés ou anomalies
- `db.py` : gère la base de données SQLite (appareils connus, événements)
- `app.py` : serveur Flask qui affiche le dashboard, avec un thread séparé
  qui exécute le scan en boucle en arrière-plan
- `config.py` : tous les paramètres modifiables du projet

## Prérequis

- Raspberry Pi 4 (ou tout ordinateur Linux) connecté au réseau à surveiller
- Python 3.9 ou plus récent
- Accès administrateur (`sudo`), requis par Scapy

## Installation

    git clone https://github.com/<ton-nom-utilisateur>/pi-network-monitor.git
    cd pi-network-monitor
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Configuration

Ouvre `config.py` et ajuste `NETWORK_RANGE` selon ton réseau. Pour trouver
ta plage réseau :

    ip addr show

## Utilisation

    sudo venv/bin/python3 app.py

Puis ouvre un navigateur à l'adresse `http://<ip_du_raspberry>:5000`.

## Tests

Tester le scanner seul, sans Flask :

    sudo venv/bin/python3 scanner.py

Tester la détection sans réseau réel :

    python3 -c "
    import db, detector
    db.init_db()
    faux_scan = [{'ip': '192.168.1.99', 'mac': 'AA:BB:CC:DD:EE:FF', 'hostname': 'test'}]
    print(detector.process_scan(faux_scan))
    "

## Dépannage

- Erreur de permission au lancement : relancer avec `sudo`
- Aucun appareil détecté : vérifier `NETWORK_RANGE` dans `config.py`
- Dashboard inaccessible depuis un autre appareil : vérifier que
  `FLASK_HOST = "0.0.0.0"` dans `config.py`

## Auteur
Fulbert AGOSSOU
Étudiant en génie électrique, concentration génie informatique — UQTR
