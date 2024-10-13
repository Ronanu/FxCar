import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline

# Parameter für die Definition des Tetraeders
breite = 2  # Länge der Seite entlang der X-Achse (v1-v2)
höhe = 1    # Höhe der Spitze über der XY-Ebene (v4)
länge = 1.5  # Abstand des dritten Punktes von der X-Achse in der XY-Ebene (v3)
spitzen_versatz = 0.5  # Position der Spitze entlang der Y-Achse (v4)
bauchfaktor = -0.1  # Faktor, um die Mittelpunkte nach außen zu bewegen

num_points = 100  # Anzahl der Punkte entlang jeder Kante

# Definiere die Punkte für die Ecken des Tetraeders
v1 = np.array([-breite / 2, 0, 0])
v2 = np.array([breite / 2, 0, 0])
v3 = np.array([0, länge, 0])
v4 = np.array([0, spitzen_versatz, höhe])

# Berechne die Mittelpunkte der Kanten
m12 = (v1 + v2) / 2  # Mittelpunkt zwischen v1 und v2
m13 = (v1 + v3) / 2  # Mittelpunkt zwischen v1 und v3
m14 = (v1 + v4) / 2  # Mittelpunkt zwischen v1 und v4
m23 = (v2 + v3) / 2  # Mittelpunkt zwischen v2 und v3
m24 = (v2 + v4) / 2  # Mittelpunkt zwischen v2 und v4
m34 = (v3 + v4) / 2  # Mittelpunkt zwischen v3 und v4

# Berechne das Zentrum des Tetraeders
center = (v1 + v2 + v3 + v4) / 4

# Verschiebe die Mittelpunkte nach außen, um eine gewölbte Form zu erhalten
m12_bauched = m12 + (m12 - center) * bauchfaktor
m13_bauched = m13 + (m13 - center) * bauchfaktor
m14_bauched = m14 + (m14 - center) * bauchfaktor
m23_bauched = m23 + (m23 - center) * bauchfaktor
m24_bauched = m24 + (m24 - center) * bauchfaktor
m34_bauched = m34 + (m34 - center) * bauchfaktor

# Funktion zur Erstellung einer kubischen Spline-Kurve durch drei Punkte
def create_spline_curve(p1, pm, p2, num_points=num_points):
    # Die Punkte entlang der Kurve
    points = np.array([p1, pm, p2])
    t = np.array([0, 0.5, 1])  # Normalisierte Parameter für die drei Punkte
    
    # Interpoliere die Punkte mit einem kubischen Spline
    cs_x = CubicSpline(t, points[:, 0])
    cs_y = CubicSpline(t, points[:, 1])
    cs_z = CubicSpline(t, points[:, 2])
    
    # Erzeuge die Punkte entlang der Spline-Kurve
    t_values = np.linspace(0, 1, num_points)
    x_values = cs_x(t_values)
    y_values = cs_y(t_values)
    z_values = cs_z(t_values)
    
    return np.column_stack((x_values, y_values, z_values))

# Erzeuge die kubischen Splines für jede der sechs Außenkanten
curve1 = create_spline_curve(v1, m12_bauched, v2)
curve2 = create_spline_curve(v1, m13_bauched, v3)
curve3 = create_spline_curve(v1, m14_bauched, v4)
curve4 = create_spline_curve(v2, m23_bauched, v3)
curve5 = create_spline_curve(v2, m24_bauched, v4)
curve6 = create_spline_curve(v3, m34_bauched, v4)

# Speichere die Koordinaten der Kurven in vier Dateien, jeweils für eine Seitenfläche
def save_curves_to_file(filename, curves):
    with open(filename, 'w') as file:
        for curve in curves:
            for point in curve:
                file.write(f"{point[0]}, {point[1]}, {point[2]}\n")
            file.write("\n")  # Trenne die Kurven durch eine leere Zeile

# Speichere die Kurven in den entsprechenden Dateien
save_curves_to_file('seite_1_2_3.txt', [curve1, curve2, curve4])
save_curves_to_file('seite_2_3_4.txt', [curve4, curve5, curve6])
save_curves_to_file('seite_1_3_4.txt', [curve2, curve3, curve6])
save_curves_to_file('seite_1_2_4.txt', [curve1, curve3, curve5])

# Plotten der Kurven mit Matplotlib
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')

# Zeichne die Kurven
for curve in [curve1, curve2, curve3, curve4, curve5, curve6]:
    ax.plot(curve[:, 0], curve[:, 1], curve[:, 2], 'b-')

# Zeichne die Eckpunkte
ax.scatter(*v1, color='r', label='v1')
ax.scatter(*v2, color='g', label='v2')
ax.scatter(*v3, color='b', label='v3')
ax.scatter(*v4, color='y', label='v4')

# Zeichne die gebauchten Mittelpunkte (optional)
ax.scatter(*m12_bauched, color='cyan', label='m12_bauched')
ax.scatter(*m13_bauched, color='magenta', label='m13_bauched')
ax.scatter(*m14_bauched, color='orange', label='m14_bauched')
ax.scatter(*m23_bauched, color='purple', label='m23_bauched')
ax.scatter(*m24_bauched, color='brown', label='m24_bauched')
ax.scatter(*m34_bauched, color='pink', label='m34_bauched')

# Setze die Achsenbeschriftungen
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Gewölbtes Tetraeder mit Außenkanten')
ax.legend()
plt.show()

print("Kurvenkoordinaten erfolgreich in Dateien gespeichert und geplottet.")