import sqlite3
from datetime import datetime
from config import DATABASE_FILE


def get_connection():
    conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS known_devices (
            mac TEXT PRIMARY KEY,
            ip TEXT,
            hostname TEXT,
            first_seen TEXT,
            last_seen TEXT,
            trusted INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            mac TEXT,
            ip TEXT,
            hostname TEXT,
            description TEXT
        )
    """)

    conn.commit()
    conn.close()


def log_event(event_type, mac, ip, hostname, description):
    conn = get_connection()
    conn.execute(
        "INSERT INTO events (timestamp, event_type, mac, ip, hostname, description) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (datetime.now().isoformat(timespec="seconds"), event_type, mac, ip, hostname, description),
    )
    conn.commit()
    conn.close()


def get_known_device(mac):
    conn = get_connection()
    row = conn.execute("SELECT * FROM known_devices WHERE mac = ?", (mac,)).fetchone()
    conn.close()
    return row


def upsert_device(mac, ip, hostname, trusted=0):
    now = datetime.now().isoformat(timespec="seconds")
    conn = get_connection()
    conn.execute("""
        INSERT INTO known_devices (mac, ip, hostname, first_seen, last_seen, trusted)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(mac) DO UPDATE SET
            ip=excluded.ip,
            hostname=excluded.hostname,
            last_seen=excluded.last_seen
    """, (mac, ip, hostname, now, now, trusted))
    conn.commit()
    conn.close()


def approve_device(mac):
    conn = get_connection()
    conn.execute("UPDATE known_devices SET trusted = 1 WHERE mac = ?", (mac,))
    conn.commit()
    conn.close()


def get_all_devices():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM known_devices ORDER BY last_seen DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_events(limit=50):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
