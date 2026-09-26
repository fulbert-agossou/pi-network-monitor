import threading
import time
from datetime import datetime

from flask import Flask, render_template, redirect, url_for

from config import SCAN_INTERVAL, FLASK_HOST, FLASK_PORT
from db import init_db, get_all_devices, get_recent_events, approve_device
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


if __name__ == "__main__":
    init_db()

    thread_scan = threading.Thread(target=boucle_de_scan, daemon=True)
    thread_scan.start()

    print(f"Dashboard disponible sur http://<ip_du_raspberry>:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False)
