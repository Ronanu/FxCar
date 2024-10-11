import numpy as np
from scipy.optimize import minimize

from scipy.interpolate import interp1d
import numpy as np

class Rand:
    def __init__(self, points):
        self.points = points
        self.x_points = points[:, 0]
        self.y_points = points[:, 1]
        self.z_points = points[:, 2]
        self.center_x = np.mean(self.x_points)
        self.center_y = np.mean(self.y_points)
        self.r_points = np.sqrt((self.x_points - self.center_x)**2 + (self.y_points - self.center_y)**2)
        self.phi_points = np.arctan2(self.y_points - self.center_y, self.x_points - self.center_x)

        # Sortiere die Punkte nach ihren Winkeln
        sorted_indices = np.argsort(self.phi_points)
        self.phi_points_sorted = self.phi_points[sorted_indices]
        self.r_points_sorted = self.r_points[sorted_indices]

        # Interpolation des Radius als Funktion des Winkels
        self.radius_interp = interp1d(
            self.phi_points_sorted, 
            self.r_points_sorted, 
            kind='linear', 
            fill_value="extrapolate"
        )

    def isInside(self, x, y):
        # Berechne den Radius und Winkel des zu überprüfenden Punktes relativ zum Zentrum
        r_point = np.sqrt((x - self.center_x)**2 + (y - self.center_y)**2)
        phi_point = np.arctan2(y - self.center_y, x - self.center_x)

        # Bestimme den interpolierten Radius für den Winkel des zu prüfenden Punktes
        interpolated_radius = self.radius_interp(phi_point)

        # Wenn der Radius des Punktes kleiner oder gleich dem interpolierten Radius ist, liegt er innerhalb
        return r_point <= interpolated_radius
