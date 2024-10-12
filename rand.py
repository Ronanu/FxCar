from scipy.interpolate import interp1d, CubicSpline
import numpy as np

class Rand:
    def __init__(self, points, interpolation_type='cubic'):
        self.points = points
        self.x_points = points[:, 0]
        self.y_points = points[:, 1]
        self.z_points = points[:, 2]
        self.center_x = np.mean(self.x_points)
        self.center_y = np.mean(self.y_points)
        self.r_points = np.sqrt((self.x_points - self.center_x)**2 + (self.y_points - self.center_y)**2)
        self.phi_points = np.arctan2(self.y_points - self.center_y, self.x_points - self.center_x)

        # Sortiere die Punkte nach ihren Winkeln und entferne doppelte Werte
        sorted_indices = np.argsort(self.phi_points)
        self.phi_points_sorted = self.phi_points[sorted_indices]
        self.r_points_sorted = self.r_points[sorted_indices]
        self.z_points_sorted = self.z_points[sorted_indices]

        # Entferne duplizierte phi-Werte, um strikte Monotonie zu gewährleisten
        unique_phi, unique_indices = np.unique(self.phi_points_sorted, return_index=True)
        self.phi_points_sorted = unique_phi
        self.r_points_sorted = self.r_points_sorted[unique_indices]
        self.z_points_sorted = self.z_points_sorted[unique_indices]

        # Wähle den Interpolationstyp
        self.interpolation_type = interpolation_type.lower()
        try:
            if self.interpolation_type == 'cubic':
                # Kubische Interpolation des Radius und der Z-Koordinate als Funktion des Winkels
                self.radius_interp = CubicSpline(
                    self.phi_points_sorted, 
                    self.r_points_sorted, 
                    extrapolate=True
                )
                self.z_interp = CubicSpline(
                    self.phi_points_sorted, 
                    self.z_points_sorted, 
                    extrapolate=True
                )
            elif self.interpolation_type == 'linear':
                # Lineare Interpolation des Radius und der Z-Koordinate als Funktion des Winkels
                self.radius_interp = interp1d(
                    self.phi_points_sorted, 
                    self.r_points_sorted, 
                    kind='linear', 
                    fill_value="extrapolate"
                )
                self.z_interp = interp1d(
                    self.phi_points_sorted, 
                    self.z_points_sorted, 
                    kind='linear', 
                    fill_value="extrapolate"
                )
            else:
                raise ValueError("Unsupported interpolation type. Choose 'linear' or 'cubic'.")
        except ValueError as e:
            print(f"Fehler bei der Interpolation: {e}. Verwende lineare Interpolation.")
            # Fallback auf lineare Interpolation
            self.radius_interp = interp1d(
                self.phi_points_sorted, 
                self.r_points_sorted, 
                kind='linear', 
                fill_value="extrapolate"
            )
            self.z_interp = interp1d(
                self.phi_points_sorted, 
                self.z_points_sorted, 
                kind='linear', 
                fill_value="extrapolate"
            )

    def isInside(self, x, y):
        """
        Überprüft, ob ein Punkt (x, y) innerhalb des Randes liegt.
        """
        r_point = np.sqrt((x - self.center_x)**2 + (y - self.center_y)**2)
        phi_point = np.arctan2(y - self.center_y, x - self.center_x)

        # Bestimme den interpolierten Radius für den Winkel des zu prüfenden Punktes
        interpolated_radius = self.radius_interp(phi_point)

        # Wenn der Radius des Punktes kleiner oder gleich dem interpolierten Radius ist, liegt er innerhalb
        return r_point <= interpolated_radius

    def getPoint(self, phi):
        """
        Gibt die (x, y, z)-Koordinaten des Randpunkts für einen gegebenen Winkel phi zurück.
        """
        # Interpoliere den Radius und die Z-Koordinate für den gegebenen Winkel
        interpolated_radius = self.radius_interp(phi)
        interpolated_z = self.z_interp(phi)
        
        # Berechne die (x, y)-Koordinaten basierend auf dem interpolierten Radius
        x = self.center_x + interpolated_radius * np.cos(phi)
        y = self.center_y + interpolated_radius * np.sin(phi)
        
        return x, y, interpolated_z

    def getRadius(self, phi):
        """
        Gibt den interpolierten Radius für einen gegebenen Winkel phi zurück.
        """
        return self.radius_interp(phi)

# Test der Rand-Klasse
if __name__ == "__main__":
    # Beispielpunkte
    points = np.array([
        [0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0],
        [0.5, 0, 0.5], [0, 0.5, 0.5], [1, 0.5, 0.5], [0.5, 1, 0.5]
    ])

    # Erstelle ein Rand-Objekt mit kubischer Interpolation
    rand = Rand(points, interpolation_type='cubic')

    # Test: Überprüfe, ob ein Punkt innerhalb des Randes liegt
    test_x, test_y = 0.5, 0.5
    is_inside = rand.isInside(test_x, test_y)
    print(f"Der Punkt ({test_x}, {test_y}) liegt innerhalb des Randes: {is_inside}")

    # Test: Hole einen Punkt auf dem Rand für einen gegebenen Winkel
    phi = np.pi / 4  # 45 Grad
    x, y, z = rand.getPoint(phi)
    print(f"Punkt auf dem Rand bei phi={phi}: ({x}, {y}, {z})")

    # Test: Hole den Radius für einen gegebenen Winkel
    radius = rand.getRadius(phi)
    print(f"Interpolierter Radius bei phi={phi}: {radius}")