import numpy as np
from scipy.spatial import Delaunay
from rand import Rand
from scipy.interpolate import CubicSpline


class SurfaceEvolverInput:
    def __init__(self, rand:Rand, num_r=20):
        self.rand = rand
        self.num_radii = num_r  # Anzahl der Radialpunkte
        self.phi_values = self.rand.phi_points_sorted
        self.num_angles = len(self.phi_values)

        # Erstelle ein Gitter für Radien und Winkel (Phi), wobei die Radienwerte abhängig von Phi sind
        self.R = np.zeros((self.num_angles, self.num_radii))
        self.max_radius_list = []
        for i, phi in enumerate(self.phi_values):
            max_radius = self.rand.getRadius(phi)
            self.max_radius_list.append(max_radius)
            self.R[i, :] = np.linspace(0.2, max_radius, self.num_radii)

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

        # Berechnung der initialen Z-Werte basierend auf kubischer Spline-Interpolation
        for i in range(radii_grid.shape[0]):
            for j in range(radii_grid.shape[1]):
                phi = np.arctan2(y_coords[i, j] - self.rand.center_y, x_coords[i, j] - self.rand.center_x)

                # Holen der beiden Randpunkte und Z-Werte bei phi und phi + pi (opposite phi)
                z_phi = self.rand.getPoint(phi)[2]
                z_opposite_phi = self.rand.getPoint(phi + np.pi if phi < 0 else phi - np.pi)[2]

                # Werte an den maximalen Radien
                radius_phi = self.rand.getRadius(phi)
                radius_opposite_phi = self.rand.getRadius(phi + np.pi if phi < 0 else phi - np.pi)

                # Aktuelle Position des Punktes
                current_radius = np.sqrt((x_coords[i, j] - self.rand.center_x)**2 + (y_coords[i, j] - self.rand.center_y)**2)

                # Erstelle die kubische Spline-Interpolation für die Z-Werte
                t = np.array([-radius_opposite_phi, radius_phi])
                z_spline = CubicSpline(t, [z_opposite_phi, z_phi], bc_type='clamped')
                
                z_interpolated = z_spline(current_radius)
                
                # Setze den interpolierten Z-Wert in die z_values_init
                z_values_init[i, j] = z_interpolated

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
            # Berechne den aktuellen Radius des Vertex
            r_current = np.sqrt((vertices[i, 0] - self.rand.center_x)**2 + (vertices[i, 1] - self.rand.center_y)**2)
            phi_current = np.arctan2(vertices[i, 1] - self.rand.center_y, vertices[i, 0] - self.rand.center_x)

            # Prüfe, ob der Vertex auf dem maximalen Radius für den Winkel liegt
            max_radius = self.rand.getRadius(phi_current)
            is_fixed = np.isclose(r_current, max_radius)

            fixed_text = " fixed" if is_fixed else ""
            evolver_input.append(f"{vertex_id} {vertices[i, 0]} {vertices[i, 1]} {Z.ravel()[i]}{fixed_text}\n")
            vertex_mapping[i] = vertex_id
            vertex_id += 1

        # Edges (Kanten definieren)
        evolver_input.append("\nedges\n")
        edge_mapping = {}
        edge_id = 1
        for simplex in triangulation.simplices:
            for k in range(3):
                v1 = simplex[k]
                v2 = simplex[(k + 1) % 3]
                edge_key = (v1, v2)

                # Berechne die Radien der Endpunkte der Kante
                r1 = np.sqrt((vertices[v1, 0] - self.rand.center_x)**2 + (vertices[v1, 1] - self.rand.center_y)**2)
                r2 = np.sqrt((vertices[v2, 0] - self.rand.center_x)**2 + (vertices[v2, 1] - self.rand.center_y)**2)
                phi1 = np.arctan2(vertices[v1, 1] - self.rand.center_y, vertices[v1, 0] - self.rand.center_x)
                phi2 = np.arctan2(vertices[v2, 1] - self.rand.center_y, vertices[v2, 0] - self.rand.center_x)

                # Prüfe, ob beide Endpunkte der Kante auf dem maximalen Radius für ihren Winkel liegen
                is_fixed = np.isclose(r1, self.rand.getRadius(phi1)) and np.isclose(r2, self.rand.getRadius(phi2))
                fixed_text = " fixed" if is_fixed else ""

                # Kante nur einmal definieren
                if edge_key not in edge_mapping and (v2, v1) not in edge_mapping:
                    evolver_input.append(f"{edge_id} {vertex_mapping[v1]} {vertex_mapping[v2]}{fixed_text}\n")
                    edge_mapping[edge_key] = edge_id
                    edge_mapping[(v2, v1)] = -edge_id  # Gegenorientierte Kante
                    edge_id += 1

        # Temporäre Speicherung der Facetten
        faces = []
        for simplex in triangulation.simplices:
            v1, v2, v3 = simplex
            edge1 = edge_mapping.get((v1, v2))
            edge2 = edge_mapping.get((v2, v3))
            edge3 = edge_mapping.get((v3, v1))
            faces.append([edge1, edge2, edge3])  # Temporär speichern

        # Sortiere die Facetten und überprüfe die Kantenorientierung
        sorted_faces = []
        for face in faces:
            sorted_face = []
            for edge in face:
                # Kante bereits richtig orientiert, ansonsten negativ markieren
                if edge > 0:
                    sorted_face.append(edge)
                else:
                    sorted_face.append(edge)  # Bereits umgekehrt
            sorted_faces.append(sorted_face)

        # Füge die sortierten Facetten dem Evolver Input hinzu
        evolver_input.append("\nfaces\n")
        face_id = 1
        for face in sorted_faces:
            evolver_input.append(f"{face_id} {face[0]} {face[1]} {face[2]}\n")
            face_id += 1

        return ''.join(evolver_input)


# Beispielaufruf der Klasse
if __name__ == "__main__":
    from rand import Rand  # Beispielhafte Randklasse
    from minimal_surface import read_file  # Funktion zum Einlesen von Punkten aus einer Datei
    points, file_path = read_file(True)  # Einlesen der Punkte aus einer Datei

    # Initialisiere das Rand-Objekt mit den eingelesenen Punkten
    rand = Rand(points, interpolation_type='linear')
    surface_input_generator = SurfaceEvolverInput(rand)

    # Generieren der Evolver Input-Datei
    evolver_input_text = surface_input_generator.generate_surface_evolver_input()

    # Speichern des Inputs in eine Datei
    with open("surface_evolver_input.fe", "w") as file:
        file.write(evolver_input_text)
    print("Surface Evolver Input erfolgreich generiert.")