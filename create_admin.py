"""Create or promote a ParkSpace administrator account.

Run locally or in the Railway service console:
    python create_admin.py ADMIN_USERNAME
The password is requested interactively and is stored as a Werkzeug hash.
"""
import sys
from getpass import getpass
from datetime import datetime
from werkzeug.security import generate_password_hash
from database import get_db, init_db

def main():
    if len(sys.argv) != 2:
        print('Usage: python create_admin.py ADMIN_USERNAME')
        raise SystemExit(2)
    username = sys.argv[1].strip()
    if not username or len(username) > 24:
        print('Username must contain 1–24 characters.')
        raise SystemExit(2)
    password = getpass('Admin password (at least 8 characters): ')
    confirm = getpass('Repeat password: ')
    if len(password) < 8 or password != confirm:
        print('Passwords must match and contain at least 8 characters.')
        raise SystemExit(2)
    init_db()
    db = get_db()
    existing = db.execute('SELECT id FROM users WHERE LOWER(username)=LOWER(?)', (username,)).fetchone()
    if existing:
        db.execute("UPDATE users SET role='admin', is_active=1 WHERE id=?", (existing['id'],))
        print('Existing account promoted to administrator.')
    else:
        db.execute('INSERT INTO users(username,password_hash,created_at,role,is_active) VALUES(?,?,?,?,?)',
                   (username, generate_password_hash(password), datetime.now().isoformat(timespec='seconds'), 'admin', 1))
        print('Administrator account created.')
    if existing:
        db.execute('UPDATE users SET password_hash=? WHERE id=?', (generate_password_hash(password), existing['id']))
    db.commit()
    db.close()

if __name__ == '__main__':
    main()
