"""Database access for ParkSpace.

Uses PostgreSQL when DATABASE_URL is set (Render/Neon), otherwise SQLite
for convenient local development on Windows.
"""
import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).with_name('parkspace.db')
DB_PATH = Path(os.environ.get('PARKSPACE_DB_PATH', DEFAULT_DB_PATH))
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()


class DatabaseConnection:
    """Small compatibility layer so the app can keep using ? placeholders."""
    def __init__(self, connection, postgres=False):
        self.connection = connection
        self.postgres = postgres

    def _sql(self, sql):
        return sql.replace('?', '%s') if self.postgres else sql

    def execute(self, sql, params=()):
        if self.postgres:
            return self.connection.execute(self._sql(sql), params)
        return self.connection.execute(sql, params)

    def executemany(self, sql, params):
        if self.postgres:
            return self.connection.cursor().executemany(self._sql(sql), params)
        return self.connection.executemany(sql, params)

    def executescript(self, script):
        if self.postgres:
            for statement in script.split(';'):
                statement = statement.strip()
                if statement:
                    self.connection.execute(statement)
        else:
            self.connection.executescript(script)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


def get_db():
    if DATABASE_URL:
        # Neon provides a PostgreSQL URL. psycopg accepts postgresql:// URLs.
        url = DATABASE_URL
        if url.startswith('postgres://'):
            url = 'postgresql://' + url[len('postgres://'):]
        import psycopg
        from psycopg.rows import dict_row
        connection = psycopg.connect(url, row_factory=dict_row, connect_timeout=10)
        return DatabaseConnection(connection, postgres=True)

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return DatabaseConnection(connection, postgres=False)


def init_db():
    db = get_db()
    if db.postgres:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
          id BIGSERIAL PRIMARY KEY,
          username TEXT NOT NULL UNIQUE,
          password_hash TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username_lower ON users (LOWER(username));

        CREATE TABLE IF NOT EXISTS parking_spaces (
          id BIGSERIAL PRIMARY KEY,
          code TEXT NOT NULL UNIQUE,
          zone TEXT NOT NULL DEFAULT 'A',
          status TEXT NOT NULL DEFAULT 'available'
            CHECK(status IN ('available','occupied','inactive'))
        );

        CREATE TABLE IF NOT EXISTS reservations (
          id BIGSERIAL PRIMARY KEY,
          space_id BIGINT NOT NULL REFERENCES parking_spaces(id),
          customer_name TEXT NOT NULL DEFAULT '',
          start_time TEXT NOT NULL,
          end_time TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'active'
            CHECK(status IN ('active','cancelled')),
          created_at TEXT NOT NULL,
          user_id BIGINT REFERENCES users(id)
        );
        ALTER TABLE reservations ADD COLUMN IF NOT EXISTS user_id BIGINT REFERENCES users(id);
        ALTER TABLE reservations ADD COLUMN IF NOT EXISTS car_number TEXT NOT NULL DEFAULT '';
        CREATE INDEX IF NOT EXISTS idx_reservations_space_time
          ON reservations(space_id, start_time, end_time, status);
        CREATE INDEX IF NOT EXISTS idx_reservations_user
          ON reservations(user_id, start_time, status);
        ''')
    else:
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
        reservation_columns = {
            row['name'] for row in db.execute('PRAGMA table_info(reservations)').fetchall()
        }
        if 'user_id' not in reservation_columns:
            db.execute('ALTER TABLE reservations ADD COLUMN user_id INTEGER REFERENCES users(id)')
        if 'car_number' not in reservation_columns:
            db.execute("ALTER TABLE reservations ADD COLUMN car_number TEXT NOT NULL DEFAULT ''")
        db.executescript('''
          CREATE INDEX IF NOT EXISTS idx_reservations_space_time
            ON reservations(space_id, start_time, end_time, status);
          CREATE INDEX IF NOT EXISTS idx_reservations_user
            ON reservations(user_id, start_time, status);
        ''')

    # Retain old bookings while clearing the obsolete manually-entered name field.
    db.execute("UPDATE reservations SET customer_name='' WHERE customer_name IS NOT NULL AND customer_name<>''")

    space_count = db.execute('SELECT COUNT(*) AS count FROM parking_spaces').fetchone()['count']
    if space_count == 0:
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
