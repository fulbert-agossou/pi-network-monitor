import threading
import time
from datetime import datetime
import csv
import io

from flask import Flask, render_template, redirect, url_for, Response

from config import SCAN_INTERVAL, FLASK_HOST, FLASK_PORT
from db import init_db, get_all_devices, get_recent_events, approve_device, get_connection
from scanner import scan_network
from detector import process_scan

app = Flask(__name__)

etat_verrou = threading.Lock()
etat = {
    "dernier_scan": None,
    "nb_appareils": 0,
    "scan_en_cours": False,
}


def boucle_de_scan():
    while True:
        with etat_verrou:
            etat["scan_en_cours"] = True

        try:
            appareils = scan_network()
            process_scan(appareils)
            with etat_verrou:
                etat["dernier_scan"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                etat["nb_appareils"] = len(appareils)
        except Exception as erreur:
            print(f"[Erreur pendant le scan] {erreur}")
        finally:
            with etat_verrou:
                etat["scan_en_cours"] = False

        time.sleep(SCAN_INTERVAL)


@app.route("/")
def dashboard():
    appareils = get_all_devices()
    evenements = get_recent_events(50)

    with etat_verrou:
        info_scan = dict(etat)

    return render_template(
        "index.html",
        appareils=appareils,
        evenements=evenements,
        info_scan=info_scan,
        scan_interval=SCAN_INTERVAL,
    )


@app.route("/approuver/<mac>", methods=["POST"])
def approuver(mac):
    approve_device(mac)
    return redirect(url_for("dashboard"))

@app.route("/export")
def export_csv():
    """
    Génère un fichier CSV contenant TOUS les événements enregistrés
    (pas seulement les 50 derniers), et le renvoie au navigateur
    comme un téléchargement.
    """
    conn = get_connection()
    lignes = conn.execute("SELECT * FROM events ORDER BY id DESC").fetchall()
    conn.close()

    # io.StringIO() = un "fichier" qui vit en mémoire, pas sur le disque.
    # On écrit dedans comme si c'était un vrai fichier CSV.
    memoire = io.StringIO()
    ecrivain = csv.writer(memoire)

    # Ligne d'en-tête du CSV
    ecrivain.writerow(["id", "timestamp", "event_type", "mac", "ip", "hostname", "description"])

    # Une ligne de CSV par événement
    for ligne in lignes:
        ecrivain.writerow([
            ligne["id"], ligne["timestamp"], ligne["event_type"],
            ligne["mac"], ligne["ip"], ligne["hostname"], ligne["description"],
        ])

    # Response construit la réponse HTTP manuellement, avec les bons
    # en-têtes pour dire au navigateur "ceci est un fichier à télécharger".
    return Response(
        memoire.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=evenements.csv"},
    )

if __name__ == "__main__":
    init_db()

    thread_scan = threading.Thread(target=boucle_de_scan, daemon=True)
    thread_scan.start()

    print(f"Dashboard disponible sur http://<ip_du_raspberry>:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)
