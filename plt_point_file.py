import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tkinter import Tk, filedialog

# Funktion zum Öffnen einer Datei und Einlesen der Kurvendaten
def open_and_plot_file():
    # Erstelle ein verstecktes Tkinter-Fenster
    root = Tk()
    root.withdraw()  # Verstecke das Hauptfenster
    
    # Öffne den Dateidialog
    file_path = filedialog.askopenfilename(
        title="Wähle eine Datei zur Anzeige",
        filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
    )
    
    if not file_path:
        print("Keine Datei ausgewählt.")
        return

    # Lese die Kurvendaten aus der Datei
    curves = []
    with open(file_path, 'r') as file:
        current_curve = []
        for line in file:
            line = line.strip()
            if line:
                # Lese die Koordinaten (x, y, z) als Tupel
                point = tuple(map(float, line.split(',')))
                current_curve.append(point)
            else:
                # Wenn eine leere Zeile gefunden wird, wird die aktuelle Kurve abgeschlossen
                if current_curve:
                    curves.append(np.array(current_curve))
                    current_curve = []

        # Füge die letzte Kurve hinzu, falls die Datei nicht mit einer leeren Zeile endet
        if current_curve:
            curves.append(np.array(current_curve))

    # Überprüfen, ob Kurven erfolgreich eingelesen wurden
    if not curves:
        print("Keine gültigen Kurvendaten gefunden.")
        return

    # Plotten der Kurven mit Matplotlib
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Zeichne die Kurven
    for curve in curves:
        ax.plot(curve[:, 0], curve[:, 1], curve[:, 2], 'b-')

    # Setze die Achsenbeschriftungen
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'3D-Plot der Datei: {file_path.split("/")[-1]}')

    # Zeige den Plot
    plt.show()

# Ausführen der Funktion zur Dateiauswahl und zum Plotten
if __name__ == "__main__":
    open_and_plot_file()