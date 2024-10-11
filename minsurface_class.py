import numpy as np
from scipy.optimize import minimize
from rand import Rand  # Importiere die Rand-Klasse

class MinSurface:
    def __init__(self, points):
        self.points = points
        self.x_points = points[:, 0]
        self.y_points = points[:, 1]
        self.z_points = points[:, 2]

        # Erstelle ein Rand-Objekt, um die Randberechnungen zu verwalten
        self.rand = Rand(points)

        # Diskretisierungsparameter
        self.num_r = 50
        self.num_phi = 50
        self.r_values = np.linspace(0, np.max(self.rand.r_points), self.num_r)
        self.phi_values = np.linspace(-np.pi, np.pi, self.num_phi)
        self.R, self.Phi = np.meshgrid(self.r_values, self.phi_values)

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

        for i in range(r.shape[0]):
            for j in range(r.shape[1]):
                if self.rand.isInside(x[i, j], y[i, j]):
                    distances = np.sqrt((self.x_points - x[i, j])**2 + (self.y_points - y[i, j])**2)
                    closest_idx = np.argmin(distances)
                    Z_init[i, j] = self.z_points[closest_idx]

        return Z_init

    def optimize_surface(self):
        # Optimiert die Fläche durch Minimierung der Flächenenergie mit Dirichlet-Randbedingungen
        def surface_energy(Z_flat, R, Phi):
            Z = Z_flat.reshape(R.shape)
            dr = self.r_values[1] - self.r_values[0]
            dphi = self.phi_values[1] - self.phi_values[0]
            total_energy = 0.0

            # Schleifenbasierte Berechnung der Energie
            for i in range(1, Z.shape[0] - 1):
                for j in range(1, Z.shape[1] - 1):
                    if not np.isnan(Z[i, j]):
                        Z_r = (Z[i + 1, j] - Z[i - 1, j]) / (2 * dr)
                        Z_phi = (Z[i, j + 1] - Z[i, j - 1]) / (2 * dphi)
                        R_safe = max(R[i, j], 1e-10)  # Vermeide Division durch Null
                        energy_density = np.sqrt(1 + Z_r**2 + (Z_phi / R_safe)**2)
                        total_energy += energy_density * dr * dphi

            return total_energy

        def dirichlet_constraint(Z_flat):
            # Erzwinge, dass die Randwerte unverändert bleiben
            Z = Z_flat.reshape(self.R.shape)
            constraint_violations = []

            # Randbedingungen anwenden: Setze Randpunkte auf ihre initialen Werte
            for i in range(self.R.shape[0]):
                for j in range(self.R.shape[1]):
                    if np.isnan(self.R[i, j]):  # Nur Randpunkte betrachten
                        constraint_violations.append(Z[i, j] - self.Z_init[i, j])

            return np.array(constraint_violations)

        print("Starte die Optimierung...")
        
        # Starte die Optimierung unter Beibehaltung der Randbedingungen
        result = minimize(
            surface_energy,
            self.Z_init.ravel(),
            args=(self.R, self.Phi),
            constraints={'type': 'eq', 'fun': dirichlet_constraint},
            method='SLSQP',  # Methode, die Gleichungsbeschränkungen unterstützt
            # debug=True,  # Aktiviere Debug-Ausgaben
            options={'maxiter': 1000}
        )

        # Überprüfe, ob die Optimierung erfolgreich war
        if result.success:
            print("Optimierung erfolgreich abgeschlossen.")
            self.Z_optimized = result.x.reshape(self.R.shape)
        else:
            print(f"Optimierung fehlgeschlagen: {result.message}")

        # Debug-Ausgabe der optimierten Z-Werte (optional)
        print("Optimierte Z-Werte:")
        print(self.Z_optimized)

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
        return self.x_points, self.y_points, self.z_points  

if __name__ == "__main__":
    # run minimal_surface.py
    import os
    os.system('python minimal_surface.py')