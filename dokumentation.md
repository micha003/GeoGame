# Dokumentation für GeoGame

_Gruppe: Paul V. und Michael V._ <br>
_Datum der Abgabe: 08.07.2025_ <br>
_Kurs: if26g1_

## Introduction

Das Spiel _GeoGame_ ist ein Projekt im Rahmen des Informatik-Grundkurses Klasse 11. Es kann sowohl allein als auch zu zweit gespielt werden. Ziel des Spiels ist es, innerhalb von 7 Runden eine maximale Punktzahl zu erreichen, indem man in jeder Runde möglichst präzise die Position einer gegebenen Stadt auf einer Karte anklickt. Am Ende des Spiels werden die besten 10 Highscores angezeigt, sodass auch ein gewisser Wettbewerb vorherrscht.

Folgende [Anforderungsdefinition](https://replit.com/@micha003/GeoGame#Anforderungsdefinition_GeoGame.jpg) wurde umgesetzt.

## Setup Guide

Damit das Spiel lokal gespielt werden kann, muss man erstmal ein paar Vorbereitungen treffen.

1. Stellen Sie sicher, dass folgende Dateien im Verzeichnis vorliegen:
   - `main.py`
   - `db_setup.py`
   - `db.json`
   - `ort.csv`
   - `DeutschlandFlussKleiner.gif`
2. Führen Sie die Datei `db_setup.py` aus. Diese erstellt die Datenbankstruktur und füllt auch alle Städte ein.
3. Zum Spielen `main.py` ausführen.


## Techstack

In diesem Projekt wurde mit Python und JSON als dokumentenorientierte Datenbank gearbeitet. Ursprünglich war es zwar angedacht, dass die Datenspeicherung mithilfe von _SQLite3_ stattfindet, jedoch haben wir uns dagegen entschieden, weil die Daten die meiste Zeit statisch sind und JSON sehr angenehm mit Python zu handeln ist.

## Code-Erläuterung

### 1. `main.py`

__Importierte Module:__

|Modul|Funktion|
|:---:|:------:|
|`tkinter`|GUI|
|`json`|Datenspeicherung|
|`random`|benötigt für Kreation von zufälligen Städten in Spielen|
|`math`|Kalkulation der Punktzahl|

__Import von benötigten Daten:__

```python
with open('db.json', 'r') as file:
    # Read the file contents
    contents = file.read()

db = json.loads(contents)

# Now you can access the 'staedte' key from the dictionary
staedte = db["staedte"]
highscore = db["highscore"]
```

Hier wird die JSON-Datei gelesen vom Python-Skript und es werden die Highscores und die Städte in jeweils einem Dictionary gespeichert. Das erleichert den Zugriff auf die Daten später im Code.

__weitere globale Variablen:__

```python
# Konstanten für Umrechnung von Koordinaten
cNord = 55.1
cSued = 47.2
cWest = 5.5
cOst = 15.5

# Punktestand
punktestand = 0
```

__Hilfsfunktionen zur Umrechnung von Bild- in Geokoordinate und umgekehrt:__

|Funktion/Methode|Parameter|Rückgabewert|
|:---:|:---:|:---:|
|`InPixelWO`|bgBild, grad|Bildkoordinate (Längengrad)|
|`InPixelNS`|bgBild, grad|Bildkoordinate (Breitengrad)|
|`InGeoX`|bgBild, x|Geokoordinate (Längengrad)|
|`InGeoY`|bgBild, x|Geokoordinate (Breitengrad)|

__Klasse `KartenGUI`:__

Die Klasse erbt bereits von der Klasse Tk und hat alle Methoden zur Verfügung, die Tk (von Tkinter) hat.

|Funktion/Methode|Parameter|Rückgabewert|Anmerkungen|
|:---:|:---:|:---:|:---:|
|`__init__`|Datei, staedteliste, Fensterbreite=1000, Fensterhoehe=600|_keine_|Diese Methode wird bei jeder Instanzierung der Klasse ausgeführt. Daher werden hier entscheidende Variablen und Konstanten sowohl für die Spiellogik als auch für die GUI definiert.|
|`btnCloseClick`|self, event|_keine_|Das ist die Methode für den _Ende_-Knopf oben, um das Spiel vorzeitig zu beenden.|
|`get_current_player_name`|self|Spielername, der aktuell an der Reihe ist|Diese Methode ist dafür gedacht, um den aktuellen Spielernamen zu ermitteln (nur gebraucht im Multiplayer-Modus).|
|`add_points_to_current_player`|self, points|_keine_|Diese Methode fügt dem entsprechend übergebenen Spieler die Punkte.|
|`switch_player`|self|_keine_|Die Methode wird immer dann aufgerufen, wenn ein Spieler im Multiplayer-Modus seinen Tip abgegeben hat und der aktuelle "aktive" gewechselt wird.|
|`update_player_display`|self|_keine_|Hier wird immer die Anzeige für den aktuellen Spieler und die Punkteanzahl aktualisiert in der GUI.|
|`getGameMode`|self|Spielmodus als `str`|Diese Methode dient der Darstellung des Eingabedialogs bei der GUI und um den Spielmodus zu ermitteln für die bevorstehende Runde.|
|`getDifficulty`|self|Schwierigkeitsgrad als `str`|Diese Methode dient der Darstellung des Eingabedialogs bei der GUI und um den Schwierigkeitsgrad zu ermitteln für die bevorstehende Runde.|


### 2. `db_setup.py`

Dieses Skript muss nur einmal vor dem ersten Spielen des Spiels ausgeführt werden. Die Funktion hiervon ist das Auslesen der Städtedaten aus `ort.csv`, die Kategorisierung der Städte in Schwierigkeitsgrade anhand der Einwohnerzahl und das Einfügen der Daten in die `db.json`-Datei und die Strukturierung dessen, sodass auch die Highscores dort gespeichert werden können.

__Importierte Module:__

- `json` --> Speicherung der Daten in die JSON-Datei
- `pandas`--> Auslesen der Daten aus der .csv-Datei

|Funktion/Methode|Parameter|Rückgabewert|Anmerkungen|
|:---:|:---:|:---:|:---:|
|`getSchwierigkeit`|ewz|Schwierigkeitsgrad als `str`|Diese Methode dient dem Zweck, anhand der Einwohnerzahl einen passenden Schwierigkeitsgrad zurückzugeben.|

__Grundlegene Struktur der Daten in der JSON-Datei:__

```python
data = {
    "highscore": {}, 
    "staedte": {
        "extrem": {},
        "schwer": {},
        "mittel": {},
        "leicht": {},
    }
}
```

__Einsetzen aller Daten aus der csv-Datei in das `data`-Dictionary:__

```python
for index, row in df.iterrows():
  name = row['Name']
  land = row['Land'] 
  ewz = row['Einwohner']
  laenge = row['Laenge']
  breite = row['Breite']
  schwierigkeit = getSchwierigkeit(ewz)
  data["staedte"][schwierigkeit][name] = [land, ewz, laenge, breite]
```

__Dumpen der Daten in die JSON-Datei:__

```python
with open('./db.json', 'w') as f:
  json.dump(data, f, indent=4)

print("Finished inserting cities into db.json. READY TO PLAY!")
```