
In Commando Zeile eingeben um im Browser zu öffnen:python -m streamlit run main.py 

folgende Aufgaben müssen implementiert werden
   - Geburtsjahr der Personen wird angezeigt
   - Auswahlmöglichkeit für Tests, sofern mehr als ein Test bei einer Person vorliegt
   - Anzeigen des Testdatums und der gesamtem Länge der Zeitreihe in Sekunden
   - EKG-Daten werden beim Einlesen sinnvoll resampelt, um Ladezeiten zu
   - verkürzen
   - Sinnvolle Berechnung der Herzrate über den gesamten Zeitraum wird angezeigt
        (durch Erweiterung der Methode find_peaks() )
   - Nutzer:in kann sinnvollen Zeitbereich für Plots auswählen

zusatz Aufgaben 
   - Herzrate im sinnvollen gleitenden Durchschnitt als Plot anzeigen
   - Log-In Oberfläche 
   - Tabelle mit allen wichtigen Daten ausgeben
   - Anlegen einer neuen Person in die Datenbank
   - Berechnen des Maximal- bzw. Minimalpuls


Daten sind mit f=1000 Hz aufgezeichnet worden

Spalte 1: Zeit
Spalte 2: Messwerte (mV)
