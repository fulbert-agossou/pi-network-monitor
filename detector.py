from db import get_known_device, upsert_device, log_event, get_all_devices


def process_scan(appareils_trouves):
    evenements_generes = []

    devices_avant = {d["ip"]: d["mac"] for d in get_all_devices()}

    for appareil in appareils_trouves:
        ip = appareil["ip"]
        mac = appareil["mac"]
        hostname = appareil["hostname"]

        connu = get_known_device(mac)

        if connu is None:
            description = f"Nouvel appareil détecté : {hostname} ({ip}, {mac})"
            log_event("new_device", mac, ip, hostname, description)
            evenements_generes.append(description)

        elif connu["ip"] != ip:
            description = f"{hostname} ({mac}) a changé d'IP : {connu['ip']} -> {ip}"
            log_event("ip_changed", mac, ip, hostname, description)
            evenements_generes.append(description)

        if ip in devices_avant and devices_avant[ip] != mac:
            description = (
                f"ALERTE : l'IP {ip} était associée à {devices_avant[ip]} "
                f"et l'est maintenant à {mac} (possible usurpation ARP)"
            )
            log_event("possible_spoofing", mac, ip, hostname, description)
            evenements_generes.append(description)

        upsert_device(mac, ip, hostname)

    return evenements_generes
