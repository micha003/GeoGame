#help("modules")

# Importiere alles aus der tkInter-Bibliothek (Oberfläche)
from tkinter import *
import sqlite3
import pandas as pd

# Random für die Zufallszahlen
import random as r

# math für spezielle trigonometrische Funktionen (Entfernungsberechnung)
from math import *

connection = sqlite3.connect("sql_micha.db")

zuDB = pd.read_csv('ort.csv')
zuDB.to_sql('ort', connection, if_exists='append', index=False)

cursor = connection.cursor()

staedte = cursor.execute("SELECT * FROM ORT").fetchall()

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

    def __init__(self, Datei, Fensterbreite=1000, Fensterhoehe=600):

        # ✨✨✨SPIEL-LOGIK✨✨✨
        self.rundenanzahl = 7
        self.punkte = 0
        self.staedte = self.staedte_selection(self.rundenanzahl)
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

    def staedte_selection(self, anzahl):
        return r.sample(staedte, anzahl)

    def punktevergabe(self, x, y, stadt_x, stadt_y) -> int:
        # Berechnung der Distanz zwischen dem Spielertipp und der tatsächlichen Stadt
        distanz = sqrt((x - stadt_x) ** 2 + (y - stadt_y) ** 2)
        # Umrechnung der Distanz in Punkte
        # Maximale Anzahl 5 Tausend Punkte
        punkte = round(5000 / (distanz + 1))
        return punkte

    """
       btnKlick: Spielmethode
    """

    def btnKlick(self, event):

        self.lblRunde = Label(self, text=f'Runde: {self.aktuelle_runde}')
        self.lblRunde.grid(column=4, row=0, sticky=E)

        # Check if game is over
        if self.aktuelle_runde > self.rundenanzahl:
            print(f"Spiel beendet! Endpunktestand: {self.punkte}")
            return

        self.aktuelle_stadt = self.staedte[self.aktuelle_runde - 1]

        self.lblAktuelleStadt = Label(self, text=f'{self.aktuelle_stadt[0]}')
        self.lblAktuelleStadt.grid(column=1, row=0, sticky=E)

        stadt_x = self.aktuelle_stadt[3]
        stadt_y = self.aktuelle_stadt[4]

        clickX = self.canBild.canvasx(event.x)
        clickY = self.canBild.canvasy(event.y)

        # Convert pixel coordinates to geo coordinates
        geoX = InGeoX(self.bgBild, clickX)
        geoY = InGeoY(self.bgBild, clickY)

        self.punkte += self.punktevergabe(geoX, geoY, stadt_x, stadt_y)

        self.lblPunkte = Label(self, text=f"Punkte: {self.punkte}")
        self.lblPunkte.grid(column=6, row=0, sticky=E)
        # TODO: Display Punkte ✅
        # TODO: Display Stadtname ✅
        # TODO: Display Runde ✅
        # TODO: Display Punktestand ✅

        self.aktuelle_runde += 1


# Erzeuge Fenster
app = KartenGUI(Datei="DeutschlandFlussKleiner.gif",
                Fensterbreite=600,
                Fensterhoehe=750)
app.mainloop()
