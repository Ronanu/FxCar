import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt

class SurfaceEvolverInput:
    def __init__(self, rand, num_r=10, num_phi=36):
        self.rand = rand
        self.num_radii = num_r  # Anzahl der Radialpunkte
        self.num_angles = num_phi  # Anzahl der Winkelpunkte
        self.phi_values = np.linspace(-np.pi, np.pi, self.num_angles)

        # Erstelle ein Gitter für Radien und Winkel (Phi), wobei die Radienwerte abhängig von Phi sind
        self.R = np.zeros((self.num_angles, self.num_radii))
        for i, phi in enumerate(self.phi_values):
            max_radius = self.rand.getRadius(phi)
            self.R[i, :] = np.linspace(0, max_radius, self.num_radii)

        # Winkelgitter für Phi erzeugen
        self.Phi = np.tile(self.phi_values, (self.num_radii, 1)).T

        # Platzhalter für die berechneten Z-Werte
        self.Z_init = None

    def calculate_initial_surface(self):
        # Berechnet die initiale Oberfläche basierend auf den nächstgelegenen Randpunkten
        self.Z_init = self.initial_surface(self.R, self.Phi)

    def initial_surface(self, radii_grid, angle_grid):
        x_coords = radii_grid * np.cos(angle_grid) + self.rand.center_x
        y_coords = radii_grid * np.sin(angle_grid) + self.rand.center_y
        z_values_init = np.full_like(radii_grid, np.nan)

        # Berechnung der initialen Z-Werte basierend auf den nächstgelegenen Randpunkten
        for i in range(radii_grid.shape[0]):
            for j in range(radii_grid.shape[1]):
                distances = np.sqrt((self.rand.x_points - x_coords[i, j])**2 + (self.rand.y_points - y_coords[i, j])**2)
                closest_idx = np.argmin(distances)
                z_values_init[i, j] = self.rand.z_points[closest_idx]

        return z_values_init

    def generate_surface_evolver_input(self):
        if self.Z_init is None:
            self.calculate_initial_surface()

        X = self.R * np.cos(self.Phi) + self.rand.center_x
        Y = self.R * np.sin(self.Phi) + self.rand.center_y
        Z = self.Z_init

        evolver_input = []

        # Vertices
        evolver_input.append("vertices\n")
        vertices = np.column_stack((X.ravel(), Y.ravel()))  # (x, y)-Punkte erzeugen
        triangulation = Delaunay(vertices)  # Delaunay-Triangulation

        vertex_mapping = {}
        vertex_id = 1
        for i in range(vertices.shape[0]):
            evolver_input.append(f"{vertex_id} {vertices[i, 0]} {vertices[i, 1]} {Z.ravel()[i]}\n")
            vertex_mapping[i] = vertex_id
            vertex_id += 1

        # Edges und Faces basierend auf der Delaunay-Triangulation
        evolver_input.append("\nedges\n")
        edge_mapping = {}
        edge_id = 1
        for simplex in triangulation.simplices:
            for k in range(3):
                v1 = simplex[k]
                v2 = simplex[(k + 1) % 3]
                edge_key = (v1, v2)
                # Kante nur einmal definieren
                if edge_key not in edge_mapping and (v2, v1) not in edge_mapping:
                    evolver_input.append(f"{edge_id} {vertex_mapping[v1]} {vertex_mapping[v2]}\n")
                    edge_mapping[edge_key] = edge_id
                    edge_id += 1

        # Faces
        evolver_input.append("\nfaces\n")
        face_id = 1
        for simplex in triangulation.simplices:
            v1, v2, v3 = simplex
            edge1 = edge_mapping.get((v1, v2)) or edge_mapping.get((v2, v1))
            edge2 = edge_mapping.get((v2, v3)) or edge_mapping.get((v3, v2))
            edge3 = edge_mapping.get((v3, v1)) or edge_mapping.get((v1, v3))
            evolver_input.append(f"{face_id} {edge1} {edge2} {edge3}\n")
            face_id += 1

        return ''.join(evolver_input)

    def visualize_surface(self):
        """Visualisiert die Oberfläche zur Überprüfung der Delaunay-Triangulation."""
        X = self.R * np.cos(self.Phi) + self.rand.center_x
        Y = self.R * np.sin(self.Phi) + self.rand.center_y

        plt.triplot(X.ravel(), Y.ravel(), Delaunay(np.column_stack((X.ravel(), Y.ravel()))).simplices)
        plt.plot(X, Y, 'o')
        plt.title("Delaunay Triangulation Visualization")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.show()

# Beispielaufruf der Klasse
if __name__ == "__main__":
    from rand import Rand  # Beispielhafte Randklasse
    from minimal_surface import read_file  # Funktion zum Einlesen von Punkten aus einer Datei
    points, file_path = read_file()

    # Initialisiere das Rand-Objekt mit den eingelesenen Punkten
    rand = Rand(points, interpolation_type='cubic')
    surface_input_generator = SurfaceEvolverInput(rand)
    
    # Visualisierung zur Überprüfung
    surface_input_generator.visualize_surface()

    # Generieren der Evolver Input-Datei
    evolver_input_text = surface_input_generator.generate_surface_evolver_input()

    # Speichern des Inputs in eine Datei
    with open("surface_evolver_input.fe", "w") as file:
        file.write(evolver_input_text)
    print("Surface Evolver Input erfolgreich generiert.")