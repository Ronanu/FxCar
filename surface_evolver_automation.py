import subprocess
import os
from datetime import datetime
import logging

# Logausgabe standardmäßig auf das Terminal (Konsole)
log_to_file = False  # Setze auf True, um Logs in eine Datei zu schreiben
evolver_executable_path = r'C:\Evolver\evolver.exe'

# Definiere Logging-Konfiguration
if log_to_file:
    logging.basicConfig(
        filename='surface_evolver_log.log',
        filemode='a',  # 'w' to overwrite or 'a' to append
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

    def run_evolver_command(self, command):
        """Runs a command in Surface Evolver and captures the output."""
        logger.debug(f"Running Evolver command: {command}")
        try:
            process = subprocess.Popen(
                [evolver_executable_path, '-c', command, self.input_file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate(timeout=60)  # Timeout von 60 Sekunden
            if stderr:
                error_message = stderr.decode()
                logger.error(f"Error in command '{command}': {error_message}")
                raise RuntimeError(f"Evolver error: {error_message}")
            logger.debug(f"Command '{command}' output: {stdout.decode()}")
            return stdout.decode()
        except subprocess.TimeoutExpired:
            logger.error(f"Command '{command}' timed out.")
            process.kill()
            raise
        except Exception as e:
            logger.exception(f"Exception while running command '{command}': {e}")
            raise

    def optimize_surface(self):
        """Runs the optimization sequence with logging and error-checking."""
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
            self.run_evolver_command("g 7000")  # Abschluss
            logger.info("Optimization sequence completed.")
        except Exception as e:
            logger.critical(f"Optimization aborted due to an error: {e}")
            raise

    def save_output(self):
        """Saves the optimized model in the desired format with logging and error-checking."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            if self.output_format == 'off':
                output_file = f"{self.input_file_path}_{timestamp}.off"
                self.run_evolver_command(f"OOGLFILE '{output_file}'")
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
        """Diagnoses common issues that could prevent Surface Evolver commands from executing."""
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
    file_paths = ["seite_1_2_3.txt", "seite_1_2_4.txt"]
    for file_path in file_paths:
        evolver = SurfaceEvolverAutomation(file_path, output_format='OFF')
        try:
            evolver.diagnose_issues()  # Diagnose potenzieller Probleme
            evolver.optimize_surface()
            evolver.save_output()
        except Exception as e:
            logger.critical(f"Process aborted for file '{file_path}' due to: {e}")
            break  # Abbrechen bei Fehler