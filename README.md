# ParkSpace - parking reservation prototype

A small Flask web application for viewing parking spaces and making reservations.

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
