import re
from datetime import datetime
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db, init_db

app = Flask(__name__)
app.secret_key = 'parkspace-local-prototype-session-key'


@app.template_filter('datetime_local')
def datetime_local(value):
    try:
        return datetime.fromisoformat(value).strftime('%d.%m.%Y %H:%M')
    except (ValueError, TypeError):
        return value or ''


@app.context_processor
def inject_session_user():
    return {
        'current_user_id': session.get('user_id'),
        'current_username': session.get('username'),
    }


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get('user_id'):
            flash('Lai turpinātu, vispirms pieslēdzies savam kontam.', 'error')
            return redirect(url_for('login', next=request.path))
        return view(*args, **kwargs)
    return wrapped_view


def safe_next_url():
    target = request.args.get('next') or request.form.get('next', '')
    # Only allow a local path, never an external URL.
    if target.startswith('/') and not target.startswith('//'):
        return target
    return url_for('index')


@app.route('/')
def index():
    db = get_db()
    now = datetime.now().isoformat(timespec='minutes')
    spaces = db.execute('''
        SELECT p.id, p.code, p.zone, p.status,
          EXISTS (
            SELECT 1 FROM reservations r
            WHERE r.space_id=p.id AND r.status='active' AND r.end_time > ?
          ) AS has_reservation,
          (
            SELECT MIN(r.start_time) FROM reservations r
            WHERE r.space_id=p.id AND r.status='active' AND r.end_time > ?
          ) AS next_reservation_start
        FROM parking_spaces p
        ORDER BY p.zone, p.code
    ''', (now, now)).fetchall()
    db.close()
    count_free = sum(1 for space in spaces if space['status'] == 'available' and not space['has_reservation'])
    return render_template('index.html', spaces=spaces, count_free=count_free)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        if not re.fullmatch(r'[A-Za-z0-9_.-]{3,24}', username):
            flash('Lietotājvārdam jābūt 3–24 simbolus garam; izmanto burtus, ciparus, punktu, _ vai -.', 'error')
            return render_template('register.html')
        if len(password) < 6:
            flash('Parolei jābūt vismaz 6 simbolus garai.', 'error')
            return render_template('register.html')
        if password != password_confirm:
            flash('Paroles nesakrīt.', 'error')
            return render_template('register.html')

        db = get_db()
        users_before = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        try:
            cursor = db.execute(
                'INSERT INTO users(username, password_hash, created_at) VALUES(?,?,?)',
                (username, generate_password_hash(password), datetime.now().isoformat(timespec='seconds')),
            )
            user_id = cursor.lastrowid
            # Preserve reservations created in the earlier no-account prototype by assigning
            # them to the first account created after the upgrade.
            if users_before == 0:
                db.execute('UPDATE reservations SET user_id=? WHERE user_id IS NULL', (user_id,))
            db.commit()
        except Exception as exc:
            db.rollback()
            if 'UNIQUE constraint failed' in str(exc):
                flash('Šāds lietotājvārds jau ir aizņemts.', 'error')
                db.close()
                return render_template('register.html')
            db.close()
            raise
        db.close()

        session.clear()
        session['user_id'] = user_id
        session['username'] = username
        flash('Konts izveidots. Tagad vari rezervēt autostāvvietu.', 'success')
        return redirect(safe_next_url())

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db()
        user = db.execute('SELECT id, username, password_hash FROM users WHERE username=? COLLATE NOCASE', (username,)).fetchone()
        db.close()
        if user is None or not check_password_hash(user['password_hash'], password):
            flash('Lietotājvārds vai parole nav pareiza.', 'error')
            return render_template('login.html')

        session.clear()
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash('Veiksmīgi pieslēdzies.', 'success')
        return redirect(safe_next_url())

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('Tu esi izgājis no konta.', 'success')
    return redirect(url_for('index'))


@app.route('/reserve/<int:space_id>', methods=['GET', 'POST'])
@login_required
def reserve(space_id):
    db = get_db()
    space = db.execute('SELECT id, code, zone, status FROM parking_spaces WHERE id=?', (space_id,)).fetchone()
    if space is None:
        db.close()
        flash('Autostāvvietas vieta nav atrasta.', 'error')
        return redirect(url_for('index'))

    form_data = {
        'start_date': request.form.get('start_date', ''),
        'end_date': request.form.get('end_date', ''),
        'start_clock': request.form.get('start_clock', ''),
        'end_clock': request.form.get('end_clock', ''),
        'start_time': request.form.get('start_time', ''),
        'end_time': request.form.get('end_time', ''),
    }

    if request.method == 'POST':
        start_raw = form_data['start_time'].strip()
        end_raw = form_data['end_time'].strip()
        if not start_raw or not end_raw:
            db.close()
            flash('Izvēlies sākuma un beigu datumu un laiku.', 'error')
            return render_template('reserve.html', space=space, form_data=form_data)
        try:
            start, end = datetime.fromisoformat(start_raw), datetime.fromisoformat(end_raw)
        except ValueError:
            db.close()
            flash('Norādi derīgu datumu un laiku.', 'error')
            return render_template('reserve.html', space=space, form_data=form_data)

        if start <= datetime.now():
            db.close()
            flash('Rezervācijas sākumam jābūt nākotnē.', 'error')
            return render_template('reserve.html', space=space, form_data=form_data)
        if end <= start:
            db.close()
            flash('Beigu laikam jābūt vēlākam par sākuma laiku.', 'error')
            return render_template('reserve.html', space=space, form_data=form_data)
        if space['status'] != 'available':
            db.close()
            flash('Šī vieta ir aizņemta vai neaktīva un pašlaik nav pieejama rezervēšanai.', 'error')
            return render_template('reserve.html', space=space, form_data=form_data)

        conflict = db.execute('''
            SELECT id FROM reservations
            WHERE space_id=? AND status='active' AND start_time < ? AND end_time > ?
            LIMIT 1
        ''', (space_id, end.isoformat(timespec='minutes'), start.isoformat(timespec='minutes'))).fetchone()
        if conflict:
            db.close()
            flash('Šajā laika periodā vieta jau ir rezervēta. Izvēlies citu laiku vai vietu.', 'error')
            return render_template('reserve.html', space=space, form_data=form_data)

        db.execute('''
            INSERT INTO reservations(space_id, customer_name, start_time, end_time, status, created_at, user_id)
            VALUES(?, '', ?, ?, 'active', ?, ?)
        ''', (
            space_id,
            start.isoformat(timespec='minutes'),
            end.isoformat(timespec='minutes'),
            datetime.now().isoformat(timespec='minutes'),
            session['user_id'],
        ))
        db.commit()
        db.close()
        flash(f'Vieta {space["code"]} rezervēta izvēlētajam laikam.', 'success')
        return redirect(url_for('reservations'))

    db.close()
    return render_template('reserve.html', space=space, form_data=form_data)


@app.route('/reservations')
@login_required
def reservations():
    db = get_db()
    rows = db.execute('''
        SELECT r.id, r.start_time, r.end_time, r.status,
               p.code AS space_code, p.zone
        FROM reservations r
        JOIN parking_spaces p ON p.id=r.space_id
        WHERE r.user_id=?
        ORDER BY r.start_time DESC
    ''', (session['user_id'],)).fetchall()
    db.close()
    return render_template('reservations.html', reservations=rows)


@app.route('/cancel/<int:reservation_id>', methods=['POST'])
@login_required
def cancel(reservation_id):
    db = get_db()
    row = db.execute('SELECT id, user_id, status, start_time FROM reservations WHERE id=?', (reservation_id,)).fetchone()
    if row is None or row['user_id'] != session['user_id']:
        flash('Rezervācija nav atrasta tavā kontā.', 'error')
    elif row['status'] != 'active':
        flash('Šī rezervācija jau ir atcelta.', 'error')
    elif row['start_time'] <= datetime.now().isoformat(timespec='minutes'):
        flash('Sākušos vai iepriekšēju rezervāciju atcelt nevar.', 'error')
    else:
        db.execute("UPDATE reservations SET status='cancelled' WHERE id=? AND user_id=?", (reservation_id, session['user_id']))
        db.commit()
        flash('Rezervācija atcelta.', 'success')
    db.close()
    return redirect(url_for('reservations'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
