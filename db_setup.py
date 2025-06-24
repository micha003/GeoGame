# ---------------------------------------------------------------------
# 
# This script needs to be executed before playing the game for the first time

import json
import pandas as pd

df = pd.read_csv('ort.csv')

data = {"highscore": {}, "staedte":{}}
for index, row in df.iterrows():
  name = row['Name']  # Replace 'city' with the actual column name in your CSV
  land = row['Land']  # Replace 'value' with the actual column name in your CSV
  ewz = row['Einwohner']
  laenge = row['Laenge']
  breite = row['Breite']
  data["staedte"][name] = [land, ewz, laenge, breite]

print(data)

with open('./db.json', 'r+') as f:
    json.dump(data, f, indent=4)
  

print("Finished inserting cities into db.json. READY TO PLAY!")
