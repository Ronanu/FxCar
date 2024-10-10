import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog
from minsurface_class import MinSurface

# Boolean-Variable, um zu steuern, ob das tkinter-Dateiauswahlfenster verwendet werden soll
use_file_dialog = False  # Ändere auf True, um das Dateiauswahlfenster zu öffnen

# Standard-Dateipfad für die Datei 'seite_1_2_3.txt'
default_file_path = 'seite_1_2_3.txt'

# Funktion zum Einlesen der Datei
def read_file():
    # Datei wählen basierend auf der Booleschen Variable
    if use_file_dialog:
        # Erstelle ein verstecktes Tkinter-Fenster
        root = Tk()
        root.withdraw()  # Verstecke das Hauptfenster
        
        # Öffne den Dateidialog
        file_path = filedialog.askopenfilename(
            title="Wähle eine Datei zur Anzeige",
            filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")]
        )
        
        if not file_path:
            print("Keine Datei ausgewählt. Standard-Datei wird verwendet.")
            file_path = default_file_path
    else:
        file_path = default_file_path

    # Lese die Kurvendaten aus der Datei
    points = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                # Lese die Koordinaten (x, y, z) als Tupel
                point = tuple(map(float, line.split(',')))
                points.append(point)

    return np.array(points), file_path

# Hauptprogramm
if __name__ == "__main__":
    points, file_path = read_file()

    # Initialisiere das MinSurface-Objekt
    min_surface = MinSurface(points)

    # Führe die Berechnungen durch
    min_surface.calculate_initial_surface()
    min_surface.optimize_surface()

    # Holen der Punkte für den Plot
    X, Y, Z_optimized = min_surface.get_points()
    Z_initial = min_surface.get_initial_values()
    x_points, y_points, z_points = min_surface.get_boundary_points()

    # Plot der initialen Z-Werte
    fig_init = plt.figure(figsize=(12, 7))
    ax_init = fig_init.add_subplot(111, projection='3d')
    ax_init.plot_surface(X, Y, Z_initial, cmap='coolwarm', edgecolor='none', alpha=0.7)
    ax_init.scatter(x_points, y_points, z_points, color='red', label='Randpunkte')
    ax_init.set_xlabel('X')
    ax_init.set_ylabel('Y')
    ax_init.set_zlabel('Z')
    ax_init.set_title(f'Initiale Oberfläche: {file_path.split("/")[-1]}')
    ax_init.legend(['Initiale Fläche', 'Randpunkte'])


    # Plot der optimierten Minimalfläche
    fig_opt = plt.figure(figsize=(12, 7))
    ax_opt = fig_opt.add_subplot(111, projection='3d')
    ax_opt.plot_surface(X, Y, Z_optimized, cmap='viridis', edgecolor='none', alpha=0.7)
    ax_opt.scatter(x_points, y_points, z_points, color='red', label='Randpunkte')
    ax_opt.set_xlabel('X')
    ax_opt.set_ylabel('Y')
    ax_opt.set_zlabel('Z')
    ax_opt.set_title(f'Optimierte Minimalfläche: {file_path.split("/")[-1]}')
    ax_opt.legend(['Optimierte Fläche', 'Randpunkte'])
    plt.show()