import numpy as np
from scipy.optimize import minimize

class MinSurface:
    def __init__(self, points):
        self.points = points
        self.x_points = points[:, 0]
        self.y_points = points[:, 1]
        self.z_points = points[:, 2]
        self.center_x = np.mean(self.x_points)
        self.center_y = np.mean(self.y_points)
        self.r_points = np.sqrt((self.x_points - self.center_x)**2 + (self.y_points - self.center_y)**2)
        self.phi_points = np.arctan2(self.y_points - self.center_y, self.x_points - self.center_x)

        # Diskretisierungsparameter
        self.num_r = 50
        self.num_phi = 50
        self.r_values = np.linspace(0, max(self.r_points), self.num_r)
        self.phi_values = np.linspace(-np.pi, np.pi, self.num_phi)
        self.R, self.Phi = np.meshgrid(self.r_values, self.phi_values)

        # Platzhalter für die berechneten Werte
        self.Z_init = None
        self.Z_optimized = None

    def calculate_initial_surface(self):
        # Berechnet die initiale Oberfläche basierend auf den nächstgelegenen Randpunkten
        self.Z_init = self.initial_surface(self.R, self.Phi)

    def initial_surface(self, r, phi):
        x = r * np.cos(phi) + self.center_x
        y = r * np.sin(phi) + self.center_y
        Z_init = np.full_like(r, np.nan)

        for i in range(r.shape[0]):
            for j in range(r.shape[1]):
                distances = np.sqrt((self.x_points - x[i, j])**2 + (self.y_points - y[i, j])**2)
                closest_idx = np.argmin(distances)
                Z_init[i, j] = self.z_points[closest_idx]

        return Z_init

    def optimize_surface(self):
        # Optimiert die Fläche durch Minimierung der Flächenenergie
        def surface_energy(Z, R, Phi):
            Z = Z.reshape(R.shape)
            dr = self.r_values[1] - self.r_values[0]
            dphi = self.phi_values[1] - self.phi_values[0]
            Z_r = np.gradient(Z, dr, axis=0)
            Z_phi = np.gradient(Z, dphi, axis=1)
            R_safe = np.where(R == 0, 1e-10, R)
            energy_density = np.sqrt(1 + Z_r**2 + (Z_phi / R_safe)**2)
            return np.sum(energy_density) * dr * dphi

        # Starte die Optimierung
        result = minimize(
            surface_energy,
            self.Z_init.ravel(),
            args=(self.R, self.Phi),
            method='L-BFGS-B',
            options={'maxiter': 1000}
        )

        self.Z_optimized = result.x.reshape(self.R.shape)

    def get_points(self):
        # Konvertiert die Polarkoordinaten zurück zu kartesischen Koordinaten für die Darstellung
        X = self.R * np.cos(self.Phi) + self.center_x
        Y = self.R * np.sin(self.Phi) + self.center_y
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