#help("modules")

# Importiere alles aus der tkInter-Bibliothek (Oberfläche)
from tkinter import *
from tkinter import simpledialog
import json

# Random für die Zufallszahlen
import random as r

# math für spezielle trigonometrische Funktionen (Entfernungsberechnung)
from math import *

# it should work now 😃
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
       Gui-Klasse mit Karte u.a. - Erweitert für 2 Spieler Hot Seat
    """

    def __init__(self,
                 Datei,
                 staedteliste,
                 Fensterbreite=1000,
                 Fensterhoehe=600):

        # GUI-Definition
        # ==============
        Tk.__init__(self)  # TK-Konstruktor der Vaterklasse aufrufen

        # ✨✨✨SPIEL-LOGIK✨✨✨
        self.rundenanzahl = 7

        # Spielmodus auswählen (1 oder 2 Spieler)
        self.spielmodus = self.getGameMode()

        # Spieler-System basierend auf Modus
        if self.spielmodus == "2_player":
            self.spieler1_name = self.ask_username("Spieler 1")
            self.spieler2_name = self.ask_username("Spieler 2")
            self.spieler1_punkte = 0
            self.spieler2_punkte = 0
            self.aktueller_spieler = 1  # 1 oder 2
        else:
            self.spieler1_name = self.ask_username("Spieler")
            self.spieler2_name = None
            self.spieler1_punkte = 0
            self.spieler2_punkte = 0
            self.aktueller_spieler = 1

        # Get the difficulty
        schwierigkeit = self.getDifficulty()
        # Filter cities by difficulty
        filtered_cities = staedteliste.get(schwierigkeit, {})
        self.staedte = self.staedte_selection(self.rundenanzahl, filtered_cities)
        self.aktuelle_runde = 1
        self.game_ended = False

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

        # Erweiterte UI basierend auf Spielmodus
        self.lblStadt = Label(self, text="Stadt: ")
        self.lblStadt.grid(column=0, row=0, sticky=E)

        # Initialize game info labels
        self.lblAktuelleStadt = Label(
            self, text=f"{self.staedte[0][0]}")  # Show first city
        self.lblAktuelleStadt.grid(column=1, row=0, sticky=E)

        self.lblRunde = Label(self, text=f"Runde: {self.aktuelle_runde}")
        self.lblRunde.grid(column=2, row=0, sticky=E)

        if self.spielmodus == "2_player":
            # Aktueller Spieler Anzeige (nur bei 2 Spielern)
            self.lblAktuellerSpieler = Label(
                self, text=f"Spieler: {self.get_current_player_name()}", 
                bg="lightblue", font=("Arial", 10, "bold"))
            self.lblAktuellerSpieler.grid(column=3, row=0, sticky=E, padx=5)

            # Spieler 1 Punkte
            self.lblSpieler1 = Label(
                self, text=f"{self.spieler1_name}: {self.spieler1_punkte}", 
                fg="blue", font=("Arial", 9, "bold"))
            self.lblSpieler1.grid(column=4, row=0, sticky=E, padx=5)

            # Spieler 2 Punkte
            self.lblSpieler2 = Label(
                self, text=f"{self.spieler2_name}: {self.spieler2_punkte}", 
                fg="red", font=("Arial", 9, "bold"))
            self.lblSpieler2.grid(column=5, row=0, sticky=E, padx=5)

            close_column = 6
            canvas_columnspan = 7
            scrollbar_column = 7
            scrollbar_columnspan = 7
        else:
            # Einzelspieler Punkte
            self.lblSpieler1 = Label(
                self, text=f"{self.spieler1_name}: {self.spieler1_punkte}", 
                fg="blue", font=("Arial", 9, "bold"))
            self.lblSpieler1.grid(column=3, row=0, sticky=E, padx=5)

            close_column = 4
            canvas_columnspan = 5
            scrollbar_column = 5
            scrollbar_columnspan = 5

        self.btnClose = Button(self, text="Ende")
        self.btnClose.bind("<Button-1>", self.btnCloseClick)
        self.btnClose.grid(column=close_column, row=0, sticky=E)

        self.canBild.grid(columnspan=canvas_columnspan)
        self.sbary.grid(column=scrollbar_column, row=1, sticky=N + S)
        self.sbarx.grid(columnspan=scrollbar_columnspan, sticky=E + W)

        # Fenster darf nicht in der Größe geändert werden.
        # Veränderbare Fenster sind deutlich komplizierter zu bauen (vor allem durch die Scrollbars)
        self.resizable(0, 0)

    def btnCloseClick(self, event):
        self.destroy()

    def get_current_player_name(self):
        """Gibt den Namen des aktuellen Spielers zurück"""
        if self.spielmodus == "2_player":
            return self.spieler1_name if self.aktueller_spieler == 1 else self.spieler2_name
        else:
            return self.spieler1_name

    def get_current_player_points(self):
        """Gibt die Punkte des aktuellen Spielers zurück"""
        return self.spieler1_punkte if self.aktueller_spieler == 1 else self.spieler2_punkte

    def add_points_to_current_player(self, points):
        """Fügt Punkte zum aktuellen Spieler hinzu"""
        if self.aktueller_spieler == 1:
            self.spieler1_punkte += points
        else:
            self.spieler2_punkte += points

    def switch_player(self):
        """Wechselt zwischen Spieler 1 und 2 (nur im 2-Spieler-Modus)"""
        if self.spielmodus == "2_player":
            self.aktueller_spieler = 2 if self.aktueller_spieler == 1 else 1

    def update_player_display(self):
        """Aktualisiert die Anzeige der Spielerinformationen"""
        if self.spielmodus == "2_player":
            self.lblAktuellerSpieler.config(text=f"Spieler: {self.get_current_player_name()}")
            self.lblSpieler1.config(text=f"{self.spieler1_name}: {self.spieler1_punkte}")
            self.lblSpieler2.config(text=f"{self.spieler2_name}: {self.spieler2_punkte}")
        else:
            self.lblSpieler1.config(text=f"{self.spieler1_name}: {self.spieler1_punkte}")

    # SETUP THE GAME MODE
    def getGameMode(self):
        # Create a dialog to ask for game mode
        dialog = Toplevel(self)
        dialog.title("Spielmodus wählen")
        dialog.geometry("400x250")
        dialog.resizable(False, False)

        # Center the dialog on the main window
        dialog.transient(self)
        dialog.grab_set()

        result = [None]  # Use list to allow modification in nested function

        def on_submit():
            selected = var.get()
            result[0] = selected
            dialog.destroy()

        def on_cancel():
            result[0] = "1_player"  # Default value
            dialog.destroy()

        # Create UI elements
        Label(dialog, text="Wählen Sie den Spielmodus:", font=("Arial", 14, "bold")).pack(pady=20)

        var = StringVar(value="1_player")

        # Create radio buttons
        Radiobutton(dialog, text="Einzelspieler", variable=var, value="1_player", 
                   font=("Arial", 12), pady=5).pack(pady=5)
        Radiobutton(dialog, text="2 Spieler (Hot Seat)", variable=var, value="2_player", 
                   font=("Arial", 12), pady=5).pack(pady=5)

        # Create button frame for better layout
        button_frame = Frame(dialog)
        button_frame.pack(pady=20)

        Button(button_frame, text="OK", command=on_submit, font=("Arial", 12), 
               bg="lightgreen", width=8).pack(side=LEFT, padx=10)
        Button(button_frame, text="Abbrechen", command=on_cancel, font=("Arial", 12), 
               bg="lightcoral", width=8).pack(side=LEFT, padx=10)

        # Handle window close button
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        dialog.wait_window()
        return result[0] if result[0] else "1_player"

    # SETUP THE DIFFICULTY
    def getDifficulty(self):
        # Create a larger popup dialog to ask for user input
        dialog = Toplevel(self)
        dialog.title("Schwierigkeit wählen")
        dialog.geometry("500x350")
        dialog.resizable(False, False)

        # Center the dialog on the main window
        dialog.transient(self)
        dialog.grab_set()

        result = [None]  # Use list to allow modification in nested function

        def on_submit():
            selected = var.get()
            result[0] = selected
            dialog.destroy()

        def on_cancel():
            result[0] = "mittel"  # Default value
            dialog.destroy()

        # Create UI elements
        Label(dialog, text="Wählen Sie die Schwierigkeit:", font=("Arial", 14, "bold")).pack(pady=20)

        var = StringVar(value="mittel")

        # Create radio buttons with better spacing
        for difficulty in ["leicht", "mittel", "schwer", "extrem"]:
            Radiobutton(dialog, text=difficulty.capitalize(), variable=var, value=difficulty, 
                       font=("Arial", 12), pady=2).pack(pady=3)

        # Create button frame for better layout
        button_frame = Frame(dialog)
        button_frame.pack(pady=20)

        Button(button_frame, text="OK", command=on_submit, font=("Arial", 12), 
               bg="lightgreen", width=8).pack(side=LEFT, padx=10)
        Button(button_frame, text="Abbrechen", command=on_cancel, font=("Arial", 12), 
               bg="lightcoral", width=8).pack(side=LEFT, padx=10)

        # Handle window close button
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        dialog.wait_window()
        return result[0] if result[0] else "mittel"

# ---------------------------------------------------------------------------
# ✨✨✨Spiel-Logik✨✨✨ (part 2 eigentlich)

    def ask_username(self, prompt="Spitzname"):
        # Create a popup dialog to ask for user input
        user_input = simpledialog.askstring("Spielername", f"{prompt} eingeben:")

        # Check if the user provided input
        if user_input is not None:
            nickname = user_input
            return nickname
        else:
            print("User cancelled the input.")
            exit(-1)

    def highscore(self, nickname, punkte):
        # Load existing data from db.json
        try:
            with open("db.json", "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {"highscore": {}, "staedte": {}}

        # Add new score
        data["highscore"][nickname] = punkte

        # Save back to db.json
        with open("db.json", "w") as file:
            json.dump(data, file, indent=4)

    def getTOP10(self):
        try:
            with open("db.json", "r") as db_file:
                data = json.load(db_file)
                highscore = data.get("highscore", {})
                print("Highscore geladen")

                # Convert dictionary to list of tuples (name, score) and sort by score (descending)
                sorted_scores = sorted(highscore.items(),
                                       key=lambda x: x[1],
                                       reverse=True)

                # Take top 10 (or less if not enough scores)
                top10 = sorted_scores[:10]

                return top10
        except (FileNotFoundError, json.JSONDecodeError):
            print("No highscore data found")
            return []

    def display_top10(self):
        """Display the top 10 high scores in a new window"""
        top10 = self.getTOP10()

        # Create a new window for the high scores
        highscore_window = Toplevel(self)
        highscore_window.title("Top 10 High Scores")
        highscore_window.geometry("350x400")
        highscore_window.resizable(False, False)

        # Title label
        title_label = Label(highscore_window,
                            text="! TOP 10 HIGH SCORES !",
                            font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # Display each score
        if top10:
            for i, (name, score) in enumerate(top10, 1):
                score_text = f"{i}. {name}: {score} Punkte"
                score_label = Label(highscore_window,
                                    text=score_text,
                                    font=("Arial", 10))
                score_label.pack(pady=2)
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

    def display_final_results(self):
        """Zeigt die Endergebnisse an (angepasst für Einzelspieler und 2-Spieler)"""
        # Create a new window for the final results
        result_window = Toplevel(self)
        result_window.title("Spielergebnisse")
        result_window.geometry("400x300")
        result_window.resizable(False, False)

        # Title label
        title_label = Label(result_window,
                            text="SPIELERGEBNISSE",
                            font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        if self.spielmodus == "2_player":
            # Determine winner for 2-player mode
            if self.spieler1_punkte > self.spieler2_punkte:
                winner = self.spieler1_name
                winner_color = "green"
            elif self.spieler2_punkte > self.spieler1_punkte:
                winner = self.spieler2_name
                winner_color = "green"
            else:
                winner = "Unentschieden!"
                winner_color = "orange"

            # Winner announcement
            winner_label = Label(result_window,
                                text=f"Gewinner: {winner}",
                                font=("Arial", 14, "bold"),
                                fg=winner_color)
            winner_label.pack(pady=10)

            # Player scores
            score1_label = Label(result_window,
                                text=f"{self.spieler1_name}: {self.spieler1_punkte} Punkte",
                                font=("Arial", 12),
                                fg="blue")
            score1_label.pack(pady=5)

            score2_label = Label(result_window,
                                text=f"{self.spieler2_name}: {self.spieler2_punkte} Punkte",
                                font=("Arial", 12),
                                fg="red")
            score2_label.pack(pady=5)
        else:
            # Single player result
            score_label = Label(result_window,
                               text=f"{self.spieler1_name}: {self.spieler1_punkte} Punkte",
                               font=("Arial", 14, "bold"),
                               fg="blue")
            score_label.pack(pady=20)

        # Button frame
        button_frame = Frame(result_window)
        button_frame.pack(pady=20)

        # Save scores button
        save_button = Button(button_frame,
                            text="Score(s) speichern",
                            command=self.save_scores,
                            font=("Arial", 10),
                            bg="lightblue")
        save_button.pack(side=LEFT, padx=10)

        # Show highscore button
        highscore_button = Button(button_frame,
                                 text="Highscore anzeigen",
                                 command=self.display_top10,
                                 font=("Arial", 10),
                                 bg="lightgreen")
        highscore_button.pack(side=LEFT, padx=10)

        # Close button
        close_button = Button(button_frame,
                             text="Schließen",
                             command=result_window.destroy,
                             font=("Arial", 10),
                             bg="lightcoral")
        close_button.pack(side=LEFT, padx=10)

    def save_scores(self):
        """Speichert Spielergebnisse basierend auf Spielmodus"""
        if self.spielmodus == "2_player":
            self.save_both_scores()
        else:
            self.highscore(self.spieler1_name, self.spieler1_punkte)
            print(f"Score gespeichert: {self.spieler1_name}: {self.spieler1_punkte}")

    def save_both_scores(self):
        """Speichert beide Spielergebnisse"""
        self.highscore(self.spieler1_name, self.spieler1_punkte)
        self.highscore(self.spieler2_name, self.spieler2_punkte)
        print(f"Scores gespeichert: {self.spieler1_name}: {self.spieler1_punkte}, {self.spieler2_name}: {self.spieler2_punkte}")

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
        # Convert dictionary to list of tuples (name, details) with hashable tuples
        staedte_list = [(name, tuple(details)) for name, details in sl.items()]
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
       btnKlick: Spielmethode - Erweitert für 2 Spieler
    """

    def btnKlick(self, event):
        # Check if game has already ended
        if self.game_ended:
            return
    
        # Check if we still have cities left
        if self.aktuelle_runde > self.rundenanzahl:
            self.end_game()
            return
    
        self.aktuelle_stadt = self.staedte[self.aktuelle_runde - 1]
    
        # Update label text instead of creating new labels
        self.lblRunde.config(text=f'Runde: {self.aktuelle_runde}')
        self.lblAktuelleStadt.config(text=f'{self.aktuelle_stadt[0]}')
    
        stadt_x = self.aktuelle_stadt[1][2]  # longitude from tuple
        stadt_y = self.aktuelle_stadt[1][3]  # latitude from tuple
    
        clickX = self.canBild.canvasx(event.x)
        clickY = self.canBild.canvasy(event.y)
    
        # Convert pixel coordinates to geo coordinates
        geoX = InGeoX(self.bgBild, clickX)
        geoY = InGeoY(self.bgBild, clickY)
    
        # Player-specific colored circle for player guess
        if self.spielmodus == "2_player":
            player_color = "blue" if self.aktueller_spieler == 1 else "red"
            player_outline = "darkblue" if self.aktueller_spieler == 1 else "darkred"
        else:
            player_color = "blue"
            player_outline = "darkblue"
    
        # Draw player marker
        self.canBild.create_oval(clickX - 5,
                                 clickY - 5,
                                 clickX + 5,
                                 clickY + 5,
                                 fill=player_color,
                                 outline=player_outline,
                                 width=2,
                                 tags="marker")
    
        # Calculate and add points to current player
        earned_points = self.punktevergabe(geoX, geoY, stadt_x, stadt_y)
        self.add_points_to_current_player(earned_points)
    
        # Update display
        self.update_player_display()
    
        # Handle turn logic based on game mode
        if self.spielmodus == "2_player":
            # Check if both players have played this round
            if self.aktueller_spieler == 1:
                # Player 1 just played, now it's Player 2's turn
                self.switch_player()
                self.update_player_display()
            else:
                # Player 2 just played, round is complete
                # NOW show the correct city position (green marker)
                city_pixel_x = InPixelWO(self.bgBild, stadt_x)
                city_pixel_y = InPixelNS(self.bgBild, stadt_y)
    
                self.canBild.create_oval(city_pixel_x - 8,
                                         city_pixel_y - 8,
                                         city_pixel_x + 8,
                                         city_pixel_y + 8,
                                         fill="green",
                                         outline="darkgreen",
                                         width=2,
                                         tags="marker")
    
                self.switch_player()  # Back to Player 1 for next round
                self.aktuelle_runde += 1
    
                # Clear markers after both players have played
                self.after(3000, lambda: self.canBild.delete("marker"))  # Increased delay
    
                # Display the next city name if there are more rounds
                if self.aktuelle_runde <= self.rundenanzahl:
                    next_city = self.staedte[self.aktuelle_runde - 1]
                    self.lblAktuelleStadt.config(text=f'{next_city[0]}')
                    self.lblRunde.config(text=f'Runde: {self.aktuelle_runde}')
                    self.update_player_display()
                else:
                    # Game is over
                    self.end_game()
        else:
            # Single player mode - show correct position immediately
            city_pixel_x = InPixelWO(self.bgBild, stadt_x)
            city_pixel_y = InPixelNS(self.bgBild, stadt_y)
    
            self.canBild.create_oval(city_pixel_x - 8,
                                     city_pixel_y - 8,
                                     city_pixel_x + 8,
                                     city_pixel_y + 8,
                                     fill="green",
                                     outline="darkgreen",
                                     width=2,
                                     tags="marker")
    
            self.aktuelle_runde += 1
    
            # Clear markers after player has played
            self.after(2000, lambda: self.canBild.delete("marker"))
    
            # Display the next city name if there are more rounds
            if self.aktuelle_runde <= self.rundenanzahl:
                next_city = self.staedte[self.aktuelle_runde - 1]
                self.lblAktuelleStadt.config(text=f'{next_city[0]}')
                self.lblRunde.config(text=f'Runde: {self.aktuelle_runde}')
                self.update_player_display()
            else:
                # Game is over
                self.end_game()

    def end_game(self):
        """End the game and show final results"""
        if self.game_ended:
            return

        self.game_ended = True
        print(f"Spiel beendet!")

        if self.spielmodus == "2_player":
            print(f"{self.spieler1_name}: {self.spieler1_punkte} Punkte")
            print(f"{self.spieler2_name}: {self.spieler2_punkte} Punkte")
            self.lblAktuellerSpieler.config(text="Spiel beendet!")
        else:
            print(f"{self.spieler1_name}: {self.spieler1_punkte} Punkte")

        self.lblAktuelleStadt.config(text="Spiel beendet!")

        # Show final results window
        self.display_final_results()


# ---------------------------------------------------------------------------
# ✈✈✈ EXECUTION ✈✈✈

# Erzeuge Fenster
app = KartenGUI(Datei="DeutschlandFlussKleiner.gif",
                staedteliste=staedte,
                Fensterbreite=600,
                Fensterhoehe=750)
app.mainloop()