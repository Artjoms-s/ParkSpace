import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).with_name('parkspace.db')
DB_PATH = Path(os.environ.get('PARKSPACE_DB_PATH', DEFAULT_DB_PATH))


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    return db


def init_db():
    db = get_db()
    db.executescript('''
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT NOT NULL UNIQUE COLLATE NOCASE,
      password_hash TEXT NOT NULL,
      created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS parking_spaces (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      code TEXT NOT NULL UNIQUE,
      zone TEXT NOT NULL DEFAULT 'A',
      status TEXT NOT NULL DEFAULT 'available'
        CHECK(status IN ('available','occupied','inactive'))
    );

    CREATE TABLE IF NOT EXISTS reservations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      space_id INTEGER NOT NULL,
      customer_name TEXT NOT NULL DEFAULT '',
      start_time TEXT NOT NULL,
      end_time TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'active'
        CHECK(status IN ('active','cancelled')),
      created_at TEXT NOT NULL,
      user_id INTEGER,
      FOREIGN KEY(space_id) REFERENCES parking_spaces(id),
      FOREIGN KEY(user_id) REFERENCES users(id)
    );
    ''')

    # Upgrade databases created by the earlier prototype without deleting bookings.
    reservation_columns = {
        row['name'] for row in db.execute('PRAGMA table_info(reservations)').fetchall()
    }
    if 'user_id' not in reservation_columns:
        db.execute('ALTER TABLE reservations ADD COLUMN user_id INTEGER REFERENCES users(id)')

    # The new version no longer stores the manually entered customer name on bookings.
    # Keep the booking itself, but remove names from old demo reservations.
    db.execute("UPDATE reservations SET customer_name='' WHERE customer_name IS NOT NULL AND customer_name<>''")

    db.executescript('''
      CREATE INDEX IF NOT EXISTS idx_reservations_space_time
        ON reservations(space_id, start_time, end_time, status);
      CREATE INDEX IF NOT EXISTS idx_reservations_user
        ON reservations(user_id, start_time, status);
    ''')

    if db.execute('SELECT COUNT(*) FROM parking_spaces').fetchone()[0] == 0:
        db.executemany(
            'INSERT INTO parking_spaces(code, zone, status) VALUES(?,?,?)',
            [
                ('A01', 'A', 'available'), ('A02', 'A', 'occupied'),
                ('A03', 'A', 'available'), ('A04', 'A', 'available'),
                ('A05', 'A', 'occupied'), ('A06', 'A', 'available'),
                ('B01', 'B', 'available'), ('B02', 'B', 'available'),
                ('B03', 'B', 'occupied'), ('B04', 'B', 'available'),
                ('B05', 'B', 'available'), ('B06', 'B', 'available'),
            ],
        )

    db.commit()
    db.close()
