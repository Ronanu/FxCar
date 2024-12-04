import subprocess
import os
from datetime import datetime
import logging
import time

# Logausgabe standardmäßig auf das Terminal (Konsole)
log_to_file = False  # Setze auf True, um Logs in eine Datei zu schreiben
evolver_executable_path = r'C:\Evolver\evolver.exe'

# Definiere Logging-Konfiguration
if log_to_file:
    logging.basicConfig(
        filename='surface_evolver_log.log',
        filemode='a',  # 'w' zum Überschreiben oder 'a' zum Anhängen
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
else:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)

class SurfaceEvolverAutomation:
    def __init__(self, input_file_path, output_format='OFF'):
        self.input_file_path = input_file_path
        self.output_format = output_format.lower()
        logger.info(f"Initialized SurfaceEvolverAutomation with file {input_file_path} and format {output_format}")

    def run_evolver_command(self, command, timeout=60):
        """Führt einen Befehl im Surface Evolver aus und erfasst die Ausgabe."""
        logger.debug(f"Running Evolver command: {command}")
        try:
            process = subprocess.Popen(
                [evolver_executable_path, self.input_file_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Senden Sie den Befehl über die Standard-Eingabe
            stdout, stderr = process.communicate(input=f"{command}\n".encode(), timeout=timeout)
            if stderr:
                error_message = stderr.decode()
                logger.error(f"Error in command '{command}': {error_message}")
                raise RuntimeError(f"Evolver error: {error_message}")
            logger.debug(f"Command '{command}' output: {stdout.decode()}")
            return stdout.decode()
        except subprocess.TimeoutExpired:
            logger.error(f"Command '{command}' timed out after {timeout} seconds.")
            process.kill()
            raise
        except Exception as e:
            logger.exception(f"Exception while running command '{command}': {e}")
            raise


    def optimize_surface(self):
        """Führt die Optimierungssequenz mit Logging und Fehlerüberprüfung durch."""
        logger.info("Starting optimization sequence.")
        try:
            for cycle in range(10):
                logger.debug(f"Starting cycle {cycle + 1} of 10")
                for i in range(5):
                    self.run_evolver_command("V")  # Vertex Averaging
                    logger.debug(f"Completed Vertex Averaging iteration {i + 1} in cycle {cycle + 1}")
                for j in range(3):
                    self.run_evolver_command("u")  # Equiangulation
                    logger.debug(f"Completed Equiangulation iteration {j + 1} in cycle {cycle + 1}")
            self.run_evolver_command("g 1000")  # Abschluss
            logger.info("Optimization sequence completed.")
        except Exception as e:
            logger.critical(f"Optimization aborted due to an error: {e}")
            raise

    def save_output(self):
        """Speichert das optimierte Modell im gewünschten Format mit Logging und Fehlerüberprüfung."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_evolver_command('P')
        try:
            if self.output_format == 'off':
                output_file = f"{self.input_file_path}_{timestamp}.off"
                self.run_evolver_command("6")
                time.sleep(1)  # Wartezeit, um sicherzustellen, dass die Datei vollständig geschrieben wird
                self.run_evolver_command('xxx' + output_file)
                logger.info(f"Saved output as OFF file: {output_file}")
            elif self.output_format == 'stl':
                output_file = f"{self.input_file_path}_{timestamp}.stl"
                self.run_evolver_command(f"postscript '{output_file}'")
                logger.info(f"Saved output as STL file: {output_file}")
            else:
                logger.warning(f"Unknown output format specified: {self.output_format}")
            print(f"Output saved to {output_file}")
        except Exception as e:
            logger.critical(f"Failed to save output due to an error: {e}")
            raise

    def diagnose_issues(self):
        """Diagnostiziert häufige Probleme, die die Ausführung von Surface Evolver-Befehlen verhindern könnten."""
        if not os.path.exists(evolver_executable_path):
            logger.critical(f"Surface Evolver executable not found at {evolver_executable_path}")
            raise FileNotFoundError(f"Surface Evolver executable not found at {evolver_executable_path}")
        if not os.path.exists(self.input_file_path):
            logger.critical(f"Input file '{self.input_file_path}' does not exist.")
            raise FileNotFoundError(f"Input file '{self.input_file_path}' does not exist.")
        if self.output_format not in ['off', 'stl']:
            logger.critical("Invalid output format specified. Please use 'OFF' or 'STL'.")
            raise ValueError("Invalid output format specified.")
        logger.info("Diagnosis complete.")

# Hauptprogramm
if __name__ == "__main__":
    file_paths = ['surface_evolver_input.fe', 'surface_evolver_input.fe']
    for file_path in file_paths:
        evolver = SurfaceEvolverAutomation(file_path, output_format='OFF')
        try:
            evolver.diagnose_issues()  # Diagnose potenzieller Probleme
            evolver.optimize_surface()
            evolver.save_output()
        except Exception as e:
            logger.critical(f"Process aborted for file '{file_path}' due to: {e}")
            break  # Abbrechen bei Fehler
