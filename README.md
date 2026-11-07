# ParkSpace - parking reservation prototype

A small Flask web application for viewing parking spaces and making reservations.

## Run locally on Windows 10/11 (SQLite)

1. Open this project folder in File Explorer, type `cmd` in the address bar and press Enter.
2. Create a virtual environment: `py -m venv .venv`
3. Activate it: `.venv\\Scripts\\activate`
4. Install dependencies: `python -m pip install -r requirements.txt`
5. Start the app: `python app.py`
6. Open `http://127.0.0.1:5000`.

If `DATABASE_URL` is not set, the app uses the local `parkspace.db` SQLite file.

## Deploy to Render with Neon PostgreSQL

1. Create a PostgreSQL database in Neon.
2. In Render, connect this GitHub repository as a **Web Service**.
3. Use these settings:
   - Runtime: `Python 3`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
4. Add environment variables in Render:
   - `DATABASE_URL` = Neon pooled connection string (keep it secret)
   - `SECRET_KEY` = a long random secret value
5. Deploy. The database schema and initial demo parking spaces are created automatically at startup.

The app uses PostgreSQL when `DATABASE_URL` is present and SQLite otherwise. The SQL schema is initialized automatically. Existing local SQLite accounts and reservations are **not automatically copied** to Neon; the online database starts with demo parking spaces and no user accounts.

## Included functionality

- Parking-space overview and top-down layout.
- User registration and login with hashed passwords.
- Reservations linked to the signed-in user.
- Reservation overlap validation and cancellation.
- User-specific reservation list.

## Notes

- Parking-space occupancy values are demonstration data; no physical sensors are connected.
- This is a study prototype, not a production-ready parking platform.
- Never commit `.env`, `parkspace.db`, passwords, or database connection strings to GitHub.


## Administratora konts

Pēc projekta palaišanas administratora kontu izveido atsevišķi (publiskajā reģistrācijas formā administratora lomu izvēlēties nevar):

```bash
python create_admin.py admin
```

Ievadi paroli, kad programma to pieprasa. Esošu kontu ar tādu pašu lietotājvārdu šī komanda paaugstina līdz administratoram un nomaina tā paroli. Railway vidē komanda jāizpilda servisa konsolē, lai administratora konts tiktu izveidots tajā pašā datubāzē, ko izmanto publicētā lietotne.

Administratora panelī ir pieejama autostāvvietu statusu maiņa, visu rezervāciju vēsture un lietotāju kontu aktivizēšana/deaktivizēšana. Rezervēts statuss tiek noteikts no aktīvām rezervācijām un to laika intervāliem; administratora manuāli iestatāmie vietas statusi ir Brīva, Aizņemta un Slēgta.
