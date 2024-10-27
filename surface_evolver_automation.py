import subprocess
import os
from datetime import datetime

class SurfaceEvolverAutomation:
    def __init__(self, input_file_path, output_format='OFF'):
        self.input_file_path = input_file_path
        self.output_format = output_format.lower()

    def run_evolver_command(self, command):
        """ Runs a command in Surface Evolver and captures the output """
        process = subprocess.Popen(
            ['C:\Evolver\evolver', '-c', command, self.input_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if stderr:
            print("Error:", stderr.decode())
        return stdout.decode()

    def optimize_surface(self):
        """ Runs the optimization sequence """
        # Block bestehend aus 5x Vertex Averaging und 3x Equiangulation, wiederholt sich 10 Mal
        for _ in range(10):
            for _ in range(5):
                self.run_evolver_command("V")  # Vertex Averaging
            for _ in range(3):
                self.run_evolver_command("u")  # Equiangulation
        # Abschluss mit 7000 Iterationen
        self.run_evolver_command("g 7000")

    def save_output(self):
        """ Saves the optimized model in the desired format """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.output_format == 'off':
            output_file = f"{self.input_file_path}_{timestamp}.off"
            self.run_evolver_command(f"OOGLFILE '{output_file}'")
        elif self.output_format == 'stl':
            output_file = f"{self.input_file_path}_{timestamp}.stl"
            self.run_evolver_command(f"postscript '{output_file}'")
        print(f"Output saved to {output_file}")

# Beispiel: Hauptprogramm
if __name__ == "__main__":
    file_paths = ["seite_1_2_3.txt", "seite_1_2_4.txt"]
    for file_path in file_paths:
        evolver = SurfaceEvolverAutomation(file_path, output_format='OFF')
        evolver.optimize_surface()
        evolver.save_output()