import evolver
import os
from datetime import datetime

class SurfaceEvolverAutomation:
    def __init__(self, input_file_path, output_format='OFF'):
        """
        Initialisiert eine Evolver-Automatisierung für eine Eingabedatei.
        :param input_file_path: Pfad zur Eingabedatei für Surface Evolver
        :param output_format: Ausgabedateiformat (z. B. 'OFF' oder 'STL')
        """
        self.input_file_path = input_file_path
        self.output_format = output_format.lower()

    def optimize_surface(self):
        """
        Führt Surface Evolver-Befehle zur Optimierung der Oberfläche aus.
        """
        with evolver.Evolver(self.input_file_path) as E:
            # Block bestehend aus 5x Vertex Averaging und 3x Equiangulation, wiederholt sich 10 Mal
            for _ in range(10):
                for _ in range(5):
                    E.run_command("V")  # Vertex Averaging
                for _ in range(3):
                    E.run_command("u")  # Equiangulation
            
            # Abschließende Berechnung
            E.run_command("g 7000")   # 7000 Iterationen für die Oberflächenberechnung

    def save_output(self):
        """
        Speichert das optimierte Modell in das gewünschte Format.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.output_format == 'off':
            output_file = f"{self.input_file_path}_{timestamp}.off"
            E.run_command(f"OOGLFILE '{output_file}'")
        elif self.output_format == 'stl':
            output_file = f"{self.input_file_path}_{timestamp}.stl"
            E.run_command(f"postscript '{output_file}'")
        print(f"Output saved to {output_file}")

def run_evolver_on_files(file_paths, output_format='OFF'):
    """
    Läuft mehrere Eingabedateien durch und speichert das Ergebnis.
    :param file_paths: Liste der Eingabedateipfade
    :param output_format: Format für die Ausgabe (OFF oder STL)
    """
    for file_path in file_paths:
        evolver_instance = SurfaceEvolverAutomation(file_path, output_format)
        evolver_instance.optimize_surface()
        evolver_instance.save_output()

# Beispiel: Hauptprogramm
if __name__ == "__main__":
    # Beispielhafte Eingabedateien
    file_paths = [
        "seite_1_2_3.txt",
        "seite_1_2_4.txt",
    ]
    run_evolver_on_files(file_paths, output_format='OFF')
