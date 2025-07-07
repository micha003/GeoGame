
# ---------------------------------------------------------------------
#
# This script needs to be executed before playing the game for the first time

import json
import pandas as pd


def getSchwierigkeit(ewz) -> str:
  ewz = int(ewz)
  match ewz:
    case _ if ewz < 65000:
      return "extrem"
    case _ if ewz < 90000:
      return "schwer"
    case _ if ewz < 180000:
      return "mittel"
    case _ if ewz >= 180000:
      return "leicht"
    case _:
      return ""


# Auslesen der csv-Datei
df = pd.read_csv('ort.csv')

# Initialize the data structure with empty dictionaries for each difficulty level
data = {
    "highscore": {}, 
    "staedte": {
        "extrem": {},
        "schwer": {},
        "mittel": {},
        "leicht": {},
    }
}

for index, row in df.iterrows():
  name = row['Name']
  land = row['Land'] 
  ewz = row['Einwohner']
  laenge = row['Laenge']
  breite = row['Breite']
  schwierigkeit = getSchwierigkeit(ewz)
  data["staedte"][schwierigkeit][name] = [land, ewz, laenge, breite]

print(data)

with open('./db.json', 'w') as f:
  json.dump(data, f, indent=4)

print("Finished inserting cities into db.json. READY TO PLAY!")
