# ParkSpace — autostāvvietu rezervēšanas prototips

Neliela Flask tīmekļa lietojumprogramma autostāvvietu apskatei un rezervēšanai.

## Iekļautās funkcijas

- Autostāvvietu pārskats un izkārtojums no augšas uz leju.
- Lietotāju reģistrācija un pieteikšanās ar hashētiem parolēm.
- Rezervācijas, kas saistītas ar pieteikušos lietotāju.
- Rezervāciju pārklāšanās pārbaude un atcelšana.
- Lietotājam specifisks rezervāciju saraksts.

## Piezīmes

- Autostāvvietu aizņemamības rādītāji ir demonstrācijas dati; nav pieslēgti fiziski sensori.
- Šis ir izpētes prototips, nevis ražošanai gatava autostāvvietu platforma.
- Nekad neievietojiet GitHubā failus `.env`, `parkspace.db`, paroles vai datubāzes savienojuma virknes.

## Administratora konts

Administratora panelī ir pieejama autostāvvietu statusu maiņa, visu rezervāciju vēsture un lietotāju kontu aktivizēšana/deaktivizēšana. Rezervēts statuss tiek noteikts no aktīvām rezervācijām un to laika intervāliem; administratora manuāli iestatāmie vietas statusi ir Brīva, Aizņemta un Slēgta.
