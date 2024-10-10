import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from tkinter import Tk, filedialog

# Funktion zum Öffnen einer Datei und Einlesen der Kurvendaten
def open_and_plot_minimal_surface():
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

    # Definiere die Flächenenergie als zu minimierende Funktion
    def surface_energy(Z, R, Phi):
        # Z wird als 1D-Array übergeben, daher Reshape
        Z = Z.reshape(R.shape)
        
        # Berechne die partiellen Ableitungen der Fläche nach r und phi
        Z_r = np.gradient(Z, R, axis=0)
        Z_phi = np.gradient(Z, Phi, axis=1)
        
        # Berechne die Normale und die Energie
        energy_density = np.sqrt(1 + Z_r**2 + (Z_phi / R)**2)
        
        # Integriere über die Fläche, um die Gesamtenergie zu berechnen
        return np.sum(energy_density) * (R[1, 0] - R[0, 0]) * (Phi[0, 1] - Phi[0, 0])

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

    # Plotten der optimierten Minimalfläche
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z_optimized, cmap='viridis', edgecolor='none')
    ax.scatter(x_points, y_points, z_points, color='red', label='Randpunkte')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(f'Optimierte Minimalfläche: {file_path.split("/")[-1]}')
    plt.legend()
    plt.show()

# Ausführen der Funktion zur Dateiauswahl und zum Plotten der Minimalfläche
if __name__ == "__main__":
    open_and_plot_minimal_surface()