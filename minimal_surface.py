import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tkinter import Tk, filedialog

# Boolean-Variable, um zu steuern, ob das tkinter-Dateiauswahlfenster verwendet werden soll
use_file_dialog = False  # Ändere auf True, um das Dateiauswahlfenster zu öffnen

# Standard-Dateipfad für die Datei 'seite_1_2_3.txt'
default_file_path = 'seite_1_2_3.txt'

# Funktion zum Öffnen einer Datei und Einlesen der Kurvendaten
def open_and_plot_minimal_surface():
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

    points = np.array(points)
    x_points = points[:, 0]
    y_points = points[:, 1]
    z_points = points[:, 2]

    # Berechnung des Mittelpunkts als Zentrum der Parameterdarstellung
    center_x = np.mean(x_points)
    center_y = np.mean(y_points)

    # Berechne r und phi für jeden Randpunkt
    r_points = np.sqrt((x_points - center_x)**2 + (y_points - center_y)**2)
    phi_points = np.arctan2(y_points - center_y, x_points - center_x)

    # Definiere eine Funktion für die Initialisierung der Höhen (z) der Fläche
    def initial_surface(r, phi):
        # Eine einfache lineare Interpolation als Startwert
        return np.interp(phi, phi_points, z_points)

    # Diskretisierungsparameter
    num_r = 50
    num_phi = 50
    r_values = np.linspace(0, max(r_points), num_r)
    phi_values = np.linspace(-np.pi, np.pi, num_phi)

    # Erzeuge ein Gitter für r und phi
    R, Phi = np.meshgrid(r_values, phi_values)

    # Initialisiere die Höhe (z) mit der Funktion
    Z_init = initial_surface(R, Phi)

    # Speichere die initialen Z-Werte zur späteren Darstellung
    Z_initial_saved = Z_init.copy()

    # Definiere die Flächenenergie als zu minimierende Funktion
    def surface_energy(Z, R, Phi):
        # Z wird als 1D-Array übergeben, daher Reshape
        Z = Z.reshape(R.shape)
        
        # Berechne die Schrittweite
        dr = r_values[1] - r_values[0]
        dphi = phi_values[1] - phi_values[0]

        # Berechne die partiellen Ableitungen der Fläche nach r und phi
        Z_r = np.gradient(Z, dr, axis=0)
        Z_phi = np.gradient(Z, dphi, axis=1)
        
        # Vermeide Division durch Null bei kleinen R-Werten
        R_safe = np.where(R == 0, 1e-10, R)  # Ersetze 0 durch einen kleinen Wert
        
        # Berechne die Normale und die Energie
        energy_density = np.sqrt(1 + Z_r**2 + (Z_phi / R_safe)**2)
        
        # Integriere über die Fläche, um die Gesamtenergie zu berechnen
        return np.sum(energy_density) * dr * dphi

    # Optimierungsfunktion, um die Fläche zu minimieren
    result = minimize(
        surface_energy,
        Z_init.ravel(),  # Flächenhöhe als 1D-Array
        args=(R, Phi),
        method='L-BFGS-B',  # Ein stabiler Optimierungsalgorithmus
        options={'maxiter': 1000}
    )

    # Extrahiere das optimierte Z aus dem Ergebnis
    Z_optimized = result.x.reshape(R.shape)

    # Konvertiere die Polarkoordinaten zurück zu kartesischen Koordinaten für die Darstellung
    X = R * np.cos(Phi) + center_x
    Y = R * np.sin(Phi) + center_y

    # Erstelle den Plot der initialen Z-Werte
    fig_init = plt.figure(figsize=(12, 7))
    ax_init = fig_init.add_subplot(111, projection='3d')
    ax_init.plot_surface(X, Y, Z_initial_saved, cmap='coolwarm', edgecolor='none', alpha=0.7)
    ax_init.scatter(x_points, y_points, z_points, color='red', label='Randpunkte')
    ax_init.set_xlabel('X')
    ax_init.set_ylabel('Y')
    ax_init.set_zlabel('Z')
    ax_init.set_title(f'Initiale Oberfläche: {file_path.split("/")[-1]}')
    ax_init.legend(['Initiale Fläche', 'Randpunkte'])
    plt.show()

    # Erstelle den Plot der optimierten Minimalfläche
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

# Ausführen der Funktion zur Dateiauswahl und zum Plotten der Minimalfläche
if __name__ == "__main__":
    open_and_plot_minimal_surface()