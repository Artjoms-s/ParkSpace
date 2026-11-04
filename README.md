# ParkSpace — prototips

Python + Flask + SQLite tīmekļa prototips autostāvvietu apskatei un rezervēšanai.

## Palaišana Windows 10/11
1. Atver projekta mapi File Explorer, adreses joslā ieraksti `cmd` un nospied Enter.
2. Izveido virtuālo vidi tikai pirmajā palaišanas reizē: `py -m venv .venv`
3. Aktivizē to: `.venv\Scripts\activate`
4. Instalē Flask tikai pirmajā reizē: `python -m pip install -r requirements.txt`
5. Palaid: `python app.py`
6. Atver `http://127.0.0.1:5000` pārlūkprogrammā.

## Darbojas
- Autostāvvietu statusu nolasīšana no SQLite datubāzes un stāvvietu plāns no augšas.
- Vienkārša kontu izveide un pieslēgšanās; paroles datubāzē tiek glabātas hešētā veidā.
- Rezervācijas izveide ar atsevišķu datuma izvēli un pulksteņa tipa laika izvēlni.
- Rezervācijas tiek piesaistītas lietotāja kontam; katrs lietotājs redz tikai savas rezervācijas.
- Pārbaude pret pārklājošām aktīvām rezervācijām un rezervācijas atcelšana.
- Esošā `parkspace.db` datubāze tiek atjaunināta automātiski; aktīvās rezervācijas netiek dzēstas.

## Datu un drošības piezīmes
- Vietu sākotnējie aizņemtības statusi ir demonstrācijas dati, reāli sensori nav pieslēgti.
- Jaunām rezervācijām nav atsevišķa vārda lauka — tās tiek piesaistītas kontam.
- Pirmā konta izveides laikā vecās rezervācijas no iepriekšējās prototipa versijas tiek piesaistītas šim kontam, lai tās nepazustu no skata.
- `parkspace.db` tiek glabāts projekta mapē. `127.0.0.1` vietne darbojas tikai tavā datorā.
- Šis ir mācību prototips, nevis sagatavota produkcijas sistēma.
