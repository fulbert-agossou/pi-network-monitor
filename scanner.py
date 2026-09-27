import socket
from scapy.all import ARP, Ether, srp, conf
from config import NETWORK_RANGE


def resolve_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        return "Inconnu"


def scan_network(ip_range=None):
    if ip_range is None:
        ip_range = NETWORK_RANGE


    paquet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range)
    reponses, _ = srp(paquet, timeout=3, verbose=False)

    appareils = []
    for envoye, recu in reponses:
        ip = recu.psrc
        mac = recu.hwsrc
        appareils.append({
            "ip": ip,
            "mac": mac,
            "hostname": resolve_hostname(ip),
        })

    return appareils


if __name__ == "__main__":
    print(f"Scan de {NETWORK_RANGE} en cours...")
    trouves = scan_network()
    print(f"{len(trouves)} appareil(s) trouvé(s) :")
    for a in trouves:
        print(f"  IP={a['ip']:<15}  MAC={a['mac']}  Hostname={a['hostname']}")
