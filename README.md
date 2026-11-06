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
