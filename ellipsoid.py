import numpy as np
import matplotlib.pyplot as plt

# Parameter für die gestauchte Ellipse
a = 3  # Länge der horizontalen Achse
b = 2  # Länge der vertikalen Achse
stauchungsfaktor = 0.8  # Stauchungsfaktor für die Ellipse

# Erzeugen der Werte für den Parameter t
t = np.linspace(0, 2*np.pi, 100)

# Berechnung der x- und y-Koordinaten der Ellipse mit Stauchung
x = a * np.cos(t) * stauchungsfaktor
y = b * np.sin(t)

# Plotten der gestauchten Ellipse
plt.figure(figsize=(8, 6))
plt.plot(x, y)

plt.xlabel('x')
plt.ylabel('y')
plt.title('Gestauchte Ellipse')
plt.grid(True)
plt.show()
