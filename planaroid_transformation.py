import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog

class Randpunkte:
    def __init__(self, file_path=None):
        if file_path is None:
            file_path = self.ask_file()
        self.points = self.load_points(file_path)

    def ask_file(self):
        root = Tk()
        root.withdraw()  # Verhindert, dass das Hauptfenster angezeigt wird
        file_path = filedialog.askopenfilename(title="Wähle die Datei mit den Randpunkten",
                                               filetypes=[("Textdateien", "*.txt"), ("Alle Dateien", "*.*")])
        if not file_path:
            raise ValueError("Keine Datei ausgewählt.")
        return file_path

    def load_points(self, file_path):
        try:
            points = np.loadtxt(file_path, delimiter=",")
        except Exception as e:
            raise ValueError(f"Fehler beim Einlesen der Datei: {e}")
        return points

class PlaneFitter:
    def __init__(self, points):
        self.points = points
        self.normal = None
        self.rotation_matrix = None

    def fit_plane(self):
        # Berechne die Normalenrichtung mittels PCA
        centroid = np.mean(self.points, axis=0)
        centered_points = self.points - centroid
        _, _, vh = np.linalg.svd(centered_points)
        self.normal = vh[-1]  # Die letzte Spalte entspricht der Normalenrichtung
        
    def calculate_rotation_matrix(self):
        if self.normal is None:
            raise ValueError("Ebene wurde noch nicht berechnet. Führe fit_plane() zuerst aus.")

        z_axis = np.array([0, 0, 1])
        axis = np.cross(self.normal, z_axis)
        axis_norm = np.linalg.norm(axis)
        if axis_norm == 0:  # Punkte sind bereits in der XY-Ebene
            self.rotation_matrix = np.eye(3)
        else:
            axis = axis / axis_norm
            angle = np.arccos(np.dot(self.normal, z_axis))
            K = np.array([
                [0, -axis[2], axis[1]],
                [axis[2], 0, -axis[0]],
                [-axis[1], axis[0], 0]
            ])
            self.rotation_matrix = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * np.dot(K, K)

    def transform_points(self):
        if self.rotation_matrix is None:
            raise ValueError("Rotationsmatrix wurde noch nicht berechnet. Führe calculate_rotation_matrix() zuerst aus.")

        centroid = np.mean(self.points, axis=0)
        centered_points = self.points - centroid
        transformed_points = np.dot(centered_points, self.rotation_matrix.T)
        return transformed_points + centroid

    def inverse_transform_points(self, transformed_points):
        if self.rotation_matrix is None:
            raise ValueError("Rotationsmatrix wurde noch nicht berechnet. Führe calculate_rotation_matrix() zuerst aus.")

        centroid = np.mean(self.points, axis=0)
        centered_points = transformed_points - centroid
        original_points = np.dot(centered_points, np.linalg.inv(self.rotation_matrix).T)
        return original_points + centroid

class Visualizer:
    @staticmethod
    def plot_points(original_points, transformed_points, reconstructed_points):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        ax.scatter(original_points[:, 0], original_points[:, 1], original_points[:, 2], c='b', label='Originalpunkte')
        ax.scatter(transformed_points[:, 0], transformed_points[:, 1], transformed_points[:, 2], c='r', label='Transformierte Punkte')
        ax.scatter(reconstructed_points[:, 0], reconstructed_points[:, 1], reconstructed_points[:, 2], c='g', label='Rücktransformiert')

        ax.legend()
        plt.show()

if __name__ == "__main__":
    randpunkte = Randpunkte()
    fitter = PlaneFitter(randpunkte.points)

    fitter.fit_plane()
    fitter.calculate_rotation_matrix()

    transformed_points = fitter.transform_points()
    reconstructed_points = fitter.inverse_transform_points(transformed_points)

    Visualizer.plot_points(randpunkte.points, transformed_points, reconstructed_points)
