import numpy as np
import matplotlib.pyplot as plt

# Parameter für die gestauchte Ellipse
a = 3  # Länge der horizontalen Achse
b = 2  # Länge der vertikalen Achse
h = 1  # Horizontaler Verschiebungsfaktor

# Parametrische Darstellung der Ellipse
t = np.linspace(0, 2*np.pi, 100)
x = a * np.cos(t)
y = b * np.sin(t) * (h * np.cos(t)+1)

ellipsenpunkte = np.array([x, y])
# plot the coordinates scaled the same

# Plotten der gestauchten Ellipse
plt.figure(figsize=(8, 8))
plt.plot(*ellipsenpunkte)
plt.gca().set_aspect('equal', adjustable='box')  # Das Seitenverhältnis beibehalten
plt.xlabel('x')
plt.ylabel('y')
plt.title('Asymmetrisch gestauchte Ellipse') 
plt.grid(True)
plt.show()
# 