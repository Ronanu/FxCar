import numpy as np
from scipy.optimize import minimize
from rand import Rand  # Importiere die Rand-Klasse

class MinSurface:
    def __init__(self, rand: Rand, num_r=10, num_phi=36):
        self.rand = rand
        self.num_r = num_r
        self.num_phi = num_phi
        self.phi_values = np.linspace(-np.pi, np.pi, self.num_phi)

        # Erstelle ein Gitter für R und Phi, wobei die R-Werte abhängig von Phi sind
        self.R = np.zeros((self.num_phi, self.num_r))
        for i, phi in enumerate(self.phi_values):
            max_r = self.rand.getRadius(phi)
            self.R[i, :] = np.linspace(0.2, max_r, self.num_r)

        # Meshgrid für R und Phi erzeugen
        self.Phi = np.tile(self.phi_values, (self.num_r, 1)).T

        # Platzhalter für die berechneten Werte
        self.Z_init = None
        self.Z_optimized = None

    def calculate_initial_surface(self):
        # Berechnet die initiale Oberfläche basierend auf den nächstgelegenen Randpunkten
        self.Z_init = self.initial_surface(self.R, self.Phi)

    def initial_surface(self, r, phi):
        x = r * np.cos(phi) + self.rand.center_x
        y = r * np.sin(phi) + self.rand.center_y
        Z_init = np.full_like(r, np.nan)

        # Berechnung der initialen Z-Werte basierend auf den nächstgelegenen Randpunkten
        for i in range(r.shape[0]):
            for j in range(r.shape[1]):
                distances = np.sqrt((self.rand.x_points - x[i, j])**2 + (self.rand.y_points - y[i, j])**2)
                closest_idx = np.argmin(distances)
                Z_init[i, j] = self.rand.z_points[closest_idx]

        return Z_init

    def optimize_surface(self):
        # Optimiert die Fläche durch Minimierung der Flächenenergie mit Dirichlet-Randbedingungen
        def surface_energy(Z_flat, R, Phi):
            Z = Z_flat.reshape(R.shape)
            total_energy = 0.0

            # Schleifenbasierte Berechnung der Energie
            for i in range(1, Z.shape[0] - 1):
                for j in range(1, Z.shape[1] - 1):
                    if not np.isnan(Z[i, j]):
                        # Berechne dr und dphi für das jeweilige Gitterelement
                        dr = (R[i, j + 1] - R[i, j - 1]) / 2.0
                        dphi = (Phi[i + 1, j] - Phi[i - 1, j]) / 2.0

                        # Berechne die Ableitungen von Z
                        Z_r = (Z[i + 1, j] - Z[i - 1, j]) / (2 * dr)
                        Z_phi = (Z[i, j + 1] - Z[i, j - 1]) / (2 * dphi)

                        # Vermeide Division durch Null in R
                        R_safe = max(R[i, j], 1e-10)

                        # Berechne die Energiedichte
                        energy_density = np.sqrt(1 + Z_r**2 + (Z_phi / R_safe)**2)
                        total_energy += energy_density * dr * dphi

            return total_energy

        print("Starte die Optimierung...")

        def reset_boundary(Z):
            # Setze die Randpunkte auf ihre initialen Werte zurück
            for i in range(self.num_phi):
                max_r_index = self.num_r - 1  # Der letzte R-Wert in der Reihe ist der maximale Radius
                Z[i, max_r_index] = self.Z_init[i, max_r_index]  # Stelle den Z-Wert am Rand wieder her
            for i in range(self.num_r):
                Z[-1, i] = Z[0, i]
            z_ring = []
            for i in range(self.num_phi):
                z_ring.append(Z[i, 0])
            z_ring_mean = np.mean(z_ring)
            for i in range(self.num_phi):
                pass #Z[i, 0] = z_ring_mean

            return Z

        # Starte die Optimierung
        Z_flat = self.Z_init.ravel()

        for iteration in range(3):  # Maximale Anzahl der Iterationen
            Z_flat = minimize(
                surface_energy,
                Z_flat,
                args=(self.R, self.Phi),
                method='SLSQP',
                options={'maxiter': 30}
            ).x

            # Reshape und Randpunkte zurücksetzen
            Z = Z_flat.reshape(self.R.shape)
            Z = reset_boundary(Z)
            Z_flat = Z.ravel()

            # Debug: Zeige Fortschritt der Optimierung
            print(f"Iteration {iteration}: Energie = {surface_energy(Z_flat, self.R, self.Phi)}")

        # Speichere das optimierte Ergebnis
        self.Z_optimized = Z
        print("Optimierung abgeschlossen.")

    def get_points(self):
        # Konvertiert die Polarkoordinaten zurück zu kartesischen Koordinaten für die Darstellung
        X = self.R * np.cos(self.Phi) + self.rand.center_x
        Y = self.R * np.sin(self.Phi) + self.rand.center_y
        return X, Y, self.Z_optimized

    def get_initial_values(self):
        # Gibt die initialen Z-Werte zurück
        return self.Z_init

    def get_boundary_points(self):
        # Gibt die Randpunkte zurück
        return self.rand.x_points, self.rand.y_points, self.rand.z_points  

if __name__ == "__main__":
    import os
    # run minimal_surface.py
    os.system("python minimal_surface.py")