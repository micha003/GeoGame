#help("modules")

# Importiere alles aus der tkInter-Bibliothek (Oberfläche)
from tkinter import *
from tkinter import simpledialog
import json

# Random für die Zufallszahlen
import random as r

# math für spezielle trigonometrische Funktionen (Entfernungsberechnung)
from math import *

# ⛔ IT DOES NOT FOR WORK ⛔
with open('db.json', 'r') as file:
    # Read the file contents
    contents = file.read()

db = json.loads(contents)

# Now you can access the 'staedte' key from the dictionary
staedte = db["staedte"]
highscore = db["highscore"]

cNord = 55.1
cSued = 47.2
cWest = 5.5
cOst = 15.5

punktestand = 0

# Hilfsfunktionen
# Die Daten in der Datenbank sind in Grad dezimal gespeichert (keine Minuten, sondern Gradanteile)


def InPixelWO(bgBild, grad):
    """ Umrechnung Geokoordinate in Bildkoordinate. Übergabe: Bild (für dessen Breite) und Längengrad """
    x = round((grad - cWest) * bgBild.width() / (cOst - cWest))
    return x


def InPixelNS(bgBild, grad):
    """ Umrechnung Geokoordinate in Bildkoordinate. Übergabe: Bild (für dessen Höhe) und Breitengrad """
    y = bgBild.height() - round(
        (grad - cSued) * bgBild.height() / (cNord - cSued))
    return y


def InGeoX(bgBild, x):
    """ Umrechnung Bildkoordinate X in Geokoordinate Laenge """
    laenge = (x / bgBild.width()) * (cOst - cWest) + cWest
    return laenge


def InGeoY(bgBild, y):
    """ Umrechnung Bildkoordinate Y in Geokoordinate Breite """
    breite = cNord - (y / bgBild.height()) * (cNord - cSued)
    return breite


###############################
############## Start Gui-Klasse


class KartenGUI(Tk):
    """
       Gui-Klasse mit Karte u.a.
    """

    def __init__(self,
                 Datei,
                 staedteliste,
                 Fensterbreite=1000,
                 Fensterhoehe=600):

        # ✨✨✨SPIEL-LOGIK✨✨✨
        self.rundenanzahl = 7
        self.punkte = 0
        self.staedte = self.staedte_selection(self.rundenanzahl, staedteliste)
        self.aktuelle_runde = 1

        # GUI-Definition
        # ==============
        Tk.__init__(self)  # TK-Konstruktor der Vaterklasse aufrufen

        # Bilddaten
        self.bgBild = PhotoImage(file="%s" % Datei)
        # Leinwand mit Scrollbars
        self.canBild = Canvas(self,
                              width=Fensterbreite,
                              height=Fensterhoehe,
                              scrollregion=(0, 0, self.bgBild.width(),
                                            self.bgBild.height()))
        self.canBild.create_image(0, 0, image=self.bgBild, anchor="nw")
        self.sbary = Scrollbar()
        self.sbary.config(command=self.canBild.yview)
        self.canBild.config(yscrollcommand=self.sbary.set)

        self.sbarx = Scrollbar()
        self.sbarx.config(command=self.canBild.xview, orient=HORIZONTAL)
        self.canBild.config(xscrollcommand=self.sbarx.set)
        self.canBild.bind('<Button-1>', self.btnKlick)

        self.lblStadt = Label(self, text="Stadt: ")
        self.lblStadt.grid(column=0, row=0, sticky=E)

        # Initialize game info labels
        self.lblAktuelleStadt = Label(
            self, text=f"{self.staedte[0][0]}")  # Show first city
        self.lblAktuelleStadt.grid(column=1, row=0, sticky=E)

        self.lblRunde = Label(self, text=f"Runde: {self.aktuelle_runde}")
        self.lblRunde.grid(column=4, row=0, sticky=E)

        self.lblPunkte = Label(self, text=f"Punkte: {self.punkte}")
        self.lblPunkte.grid(column=6, row=0, sticky=E)

        self.btnClose = Button(self, text="Ende")
        self.btnClose.bind("<Button-1>", self.btnCloseClick)
        self.btnClose.grid(column=3, row=0, sticky=E)

        self.canBild.grid(columnspan=6)
        self.sbary.grid(column=6, row=1, sticky=N + S)
        self.sbarx.grid(columnspan=6, sticky=E + W)

        # Fenster darf nicht in der Größe geändert werden.
        # Veränderbare Fenster sind deutlich komplizierter zu bauen (vor allem durch die Scrollbars)
        self.resizable(0, 0)

    def btnCloseClick(self, event):
        self.destroy()

# ---------------------------------------------------------------------------
# ✨✨✨Spiel-Logik✨✨✨ (part 2 eigentlich)

    def ask_username(self):
        # Create a popup dialog to ask for user input
        user_input = simpledialog.askstring("Spitzname", "EINGEBEN")

        # Check if the user provided input
        if user_input is not None:
            nickname = user_input
            return nickname
        else:
            print("User  cancelled the input.")
            exit(-1)

    def highscore(self, nickname, punkte):
        with open("highscore.json", "w") as file:
            data = {}
            data["highscore"][nickname] = punkte
            json.dump(data, file, indent=4)

    def getTOP5(self):
        with open("db.json", "r") as db:
            highscore = db["highscore"]
            print("Highscore geladen")

            # Convert dictionary to list of tuples (name, score) and sort by score (descending)
            sorted_scores = sorted(highscore.items(),
                                   key=lambda x: x[1],
                                   reverse=True)

            # Take top 5 (or less if not enough scores)
            top5 = sorted_scores[:5]

            return top5

    def display_top5(self):
        """Display the top 5 high scores in a new window"""
        top5 = self.getTOP5()

        # Create a new window for the high scores
        highscore_window = Toplevel(self)
        highscore_window.title("Top 5 High Scores")
        highscore_window.geometry("300x250")
        highscore_window.resizable(False, False)

        # Title label
        title_label = Label(highscore_window,
                            text="! TOP 5 HIGH SCORES !",
                            font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # Display each score
        if top5:
            for i, (name, score) in enumerate(top5, 1):
                score_text = f"{i}. {name}: {score} Punkte"
                score_label = Label(highscore_window,
                                    text=score_text,
                                    font=("Arial", 10))
                score_label.pack(pady=5)
        else:
            no_scores_label = Label(highscore_window,
                                    text="Noch keine Scores vorhanden!",
                                    font=("Arial", 10))
            no_scores_label.pack(pady=20)

        # Close button
        close_button = Button(highscore_window,
                              text="Schließen",
                              command=highscore_window.destroy)
        close_button.pack(pady=10)

    def has_duplicates(self, items):
        seen = set()
        for item in items:
            # Convert the item to a tuple if it is a list
            hashable_item = tuple(item) if isinstance(item, list) else item
            if hashable_item in seen:
                return True
            seen.add(hashable_item)
        return False

    def staedte_selection(self, anzahl, sl):
        # Convert dictionary to list of tuples (name, details)
        staedte_list = list(sl.items())
        sample = r.sample(staedte_list, anzahl)
        if self.has_duplicates(sample):
            print("Duplicates found in the sample.")
            return self.staedte_selection(anzahl, sl)
        print(sample)
        return sample

    def punktevergabe(self, x, y, stadt_x, stadt_y) -> int:
        # Berechnung der Distanz zwischen dem Spielertipp und der tatsächlichen Stadt
        distanz = sqrt((x - stadt_x)**2 + (y - stadt_y)**2)
        # Umrechnung der Distanz in Punkte
        # Maximale Anzahl 5 Tausend Punkte
        punkte = round(5000 / (distanz + 1))
        return punkte

    """
       btnKlick: Spielmethode
    """

    def btnKlick(self, event):
        self.aktuelle_stadt = self.staedte[self.aktuelle_runde - 1]

        # Update label text instead of creating new labels
        self.lblRunde.config(text=f'Runde: {self.aktuelle_runde}')
        self.lblAktuelleStadt.config(text=f'{self.aktuelle_stadt[0]}')

        stadt_x = self.aktuelle_stadt[3]
        stadt_y = self.aktuelle_stadt[4]

        clickX = self.canBild.canvasx(event.x)
        clickY = self.canBild.canvasy(event.y)

        # Convert pixel coordinates to geo coordinates
        geoX = InGeoX(self.bgBild, clickX)
        geoY = InGeoY(self.bgBild, clickY)

        # Clear previous markers (keep only the background image)
        self.canBild.delete("marker")

        # Convert city coordinates to pixel coordinates for drawing
        city_pixel_x = InPixelWO(self.bgBild, stadt_x)
        city_pixel_y = InPixelNS(self.bgBild, stadt_y)

        # Draw markers with tags for easy deletion
        # Green circle for correct city position (larger)
        self.canBild.create_oval(city_pixel_x - 8,
                                 city_pixel_y - 8,
                                 city_pixel_x + 8,
                                 city_pixel_y + 8,
                                 fill="green",
                                 outline="darkgreen",
                                 width=2,
                                 tags="marker")

        # Red circle for player guess (smaller)
        self.canBild.create_oval(clickX - 5,
                                 clickY - 5,
                                 clickX + 5,
                                 clickY + 5,
                                 fill="red",
                                 outline="darkred",
                                 width=2,
                                 tags="marker")

        self.punkte += self.punktevergabe(geoX, geoY, stadt_x, stadt_y)

        # Update points label
        self.lblPunkte.config(text=f"Punkte: {self.punkte}")

        self.aktuelle_runde += 1

        # Display the next city name if there are more rounds
        if self.aktuelle_runde <= self.rundenanzahl:
            next_city = self.staedte[self.aktuelle_runde - 1]
            self.lblAktuelleStadt.config(text=f'{next_city[0]}')
            self.lblRunde.config(text=f'Runde: {self.aktuelle_runde}')

        # Check if game is over
        if self.aktuelle_runde > self.rundenanzahl:
            print(f"Spiel beendet! Endpunktestand: {self.punkte}")
            self.nickname = self.ask_username()
            self.highscore(self.nickname, self.punkte)
            self.display_top5()

            return


# ---------------------------------------------------------------------------
# ✈✈✈ EXECUTION ✈✈✈

# Erzeuge Fenster
app = KartenGUI(Datei="DeutschlandFlussKleiner.gif",
                staedteliste=staedte,
                Fensterbreite=600,
                Fensterhoehe=750)
app.mainloop()
