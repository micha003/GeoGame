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
staedte_select = r.sample(staedte, 10)

print(staedte_select)

cNord = 55.1
cSued = 47.2
cWest = 5.5
cOst  = 15.5

punktestand = 0

# Hilfsfunktionen
# Die Daten in der Datenbank sind in Grad dezimal gespeichert (keine Minuten, sondern Gradanteile)

def InPixelWO(bgBild, grad):
    """ Umrechnung Geokoordinate in Bildkoordinate. Übergabe: Bild (für dessen Breite) und Längengrad """
    x = round((grad-cWest)* bgBild.width()/(cOst-cWest))
    return x

def InPixelNS(bgBild, grad):
    """ Umrechnung Geokoordinate in Bildkoordinate. Übergabe: Bild (für dessen Höhe) und Breitengrad """
    y = bgBild.height()-round((grad-cSued)*bgBild.height()/(cNord-cSued))
    return y


def InGeoX(bgBild,x):
    """ Umrechnung Bildkoordinate X in Geokoordinate Laenge """
    laenge = (x/bgBild.width()) * (cOst - cWest) + cWest
    return laenge

def InGeoY(bgBild,y):
    """ Umrechnung Bildkoordinate Y in Geokoordinate Breite """
    breite = cNord - (y/bgBild.height()) * (cNord - cSued)
    return breite


###############################
############## Start Gui-Klasse

class KartenGUI(Tk):
    """
       Gui-Klasse mit Karte u.a.
    """
    def __init__(self, Datei, Fensterbreite=1000, Fensterhoehe=600):

        # GUI-Definition
        # ==============
        Tk.__init__(self)  # TK-Konstruktor der Vaterklasse aufrufen

        # Bilddaten
        self.bgBild = PhotoImage(file="%s" % Datei)
        # Leinwand mit Scrollbars
        self.canBild=Canvas(self, width=Fensterbreite, height=Fensterhoehe, scrollregion=(0, 0, self.bgBild.width(), self.bgBild.height()))
        self.canBild.create_image(0,0,image=self.bgBild,anchor="nw")
        self.sbary=Scrollbar()
        self.sbary.config(command=self.canBild.yview)
        self.canBild.config(yscrollcommand=self.sbary.set)

        self.sbarx=Scrollbar()
        self.sbarx.config(command=self.canBild.xview, orient=HORIZONTAL)
        self.canBild.config(xscrollcommand=self.sbarx.set)
        self.canBild.bind('<Button-1>',self.btnKlick)


        self.lblPosition=Label(self, text="Position: ")
        self.lblPosition.grid(column=0,row=0,sticky=E)

        self.btnClose = Button(self,text="Ende")
        self.btnClose.bind("<Button-1>", self.btnCloseClick)
        self.btnClose.grid(column=3, row=0, sticky=E)

        self.canBild.grid(columnspan=6)
        self.sbary.grid(column=6,row=1, sticky=N+S)
        self.sbarx.grid(columnspan=6,sticky=E+W)

        # Fenster darf nicht in der Größe geändert werden.
        # Veränderbare Fenster sind deutlich komplizierter zu bauen (vor allem durch die Scrollbars)
        self.resizable(0,0)




    def btnCloseClick(self, event):
        self.destroy()



    def btnKlick(self,event):
        """
           Klick auf das Bild --> Anzeige der Geokoordinaten
        """
        clickX = self.canBild.canvasx(event.x)
        clickY = self.canBild.canvasy(event.y)

        ####### Hier muss noch wenig programmiert werden



############## Ende Gui-Klasse
##############################



# Erzeuge Fenster
app=KartenGUI(Datei="DeutschlandFlussKleiner.gif", Fensterbreite=600, Fensterhoehe=750)
app.mainloop()