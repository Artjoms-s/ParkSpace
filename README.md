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


## Administratora konts

Pēc projekta palaišanas administratora kontu izveido atsevišķi (publiskajā reģistrācijas formā administratora lomu izvēlēties nevar):

```bash
python create_admin.py admin
```

Ievadi paroli, kad programma to pieprasa. Esošu kontu ar tādu pašu lietotājvārdu šī komanda paaugstina līdz administratoram un nomaina tā paroli. Railway vidē komanda jāizpilda servisa konsolē, lai administratora konts tiktu izveidots tajā pašā datubāzē, ko izmanto publicētā lietotne.

Administratora panelī ir pieejama autostāvvietu statusu maiņa, visu rezervāciju vēsture un lietotāju kontu aktivizēšana/deaktivizēšana. Rezervēts statuss tiek noteikts no aktīvām rezervācijām un to laika intervāliem; administratora manuāli iestatāmie vietas statusi ir Brīva, Aizņemta un Slēgta.
