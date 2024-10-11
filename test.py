import numpy as np
import matplotlib.pyplot as plt

# Beispiel-Randpunkte
points = np.array([
    [0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0],
    [0.5, 0, 0.5], [0, 0.5, 0.5], [1, 0.5, 0.5], [0.5, 1, 0.5]
])
x_points = points[:, 0]
y_points = points[:, 1]
z_points = points[:, 2]

# Diskretisierung
num_r = 50
num_phi = 50
x_vals = np.linspace(np.min(x_points), np.max(x_points), num_r)
y_vals = np.linspace(np.min(y_points), np.max(y_points), num_phi)
X, Y = np.meshgrid(x_vals, y_vals)

# Initialisiere Z mit den Randwerten
Z = np.full_like(X, np.nan)
for i in range(num_r):
    for j in range(num_phi):
        distances = np.sqrt((x_points - X[i, j])**2 + (y_points - Y[i, j])**2)
        closest_idx = np.argmin(distances)
        Z[i, j] = z_points[closest_idx]

# Definiere Lernrate und Iterationen
alpha = 0.001  # Reduzierte Lernrate
num_iterations = 0
epsilon = 1e-8  # Kleiner regulärer Wert zur Stabilisierung

# Gradientenabstieg
for iteration in range(num_iterations):
    Z_r = (Z[2:, 1:-1] - Z[:-2, 1:-1]) / (2 * (x_vals[1] - x_vals[0]) + epsilon)
    Z_phi = (Z[1:-1, 2:] - Z[1:-1, :-2]) / (2 * (y_vals[1] - y_vals[0]) + epsilon)
    
    # Berechne die Energie
    energy = np.sqrt(1 + Z_r**2 + Z_phi**2)
    
    # Berechne den Gradienten der Energie
    gradient = np.zeros_like(Z)
    gradient[1:-1, 1:-1] = (Z[2:, 1:-1] - 2 * Z[1:-1, 1:-1] + Z[:-2, 1:-1]) / (x_vals[1] - x_vals[0])**2 + \
                           (Z[1:-1, 2:] - 2 * Z[1:-1, 1:-1] + Z[1:-1, :-2]) / (y_vals[1] - y_vals[0])**2
    
    # Normiere den Gradienten
    gradient_norm = np.linalg.norm(gradient[1:-1, 1:-1])
    if gradient_norm > 0:
        gradient[1:-1, 1:-1] /= gradient_norm

    # Update Schritt (nur für innere Punkte)
    Z[1:-1, 1:-1] -= alpha * gradient[1:-1, 1:-1]

    # Fixiere Randpunkte
    Z[0, :] = Z[1, :]
    Z[-1, :] = Z[-2, :]
    Z[:, 0] = Z[:, 1]
    Z[:, -1] = Z[:, -2]

    # Debug-Ausgabe (optional)
    if iteration % 50 == 0:
        print(f"Iteration {iteration}: Maximaler Gradient = {np.max(np.abs(gradient))}")

    # Vermeide Überlauf
    Z = np.clip(Z, -10, 10)

# Plot der optimierten Fläche
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.8)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('Optimierte Minimalfläche mit Gradientenabstieg')
plt.show()