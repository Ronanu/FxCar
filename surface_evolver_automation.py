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

    def run_evolver_session(self, commands, timeout=120):
        """Führt mehrere Befehle in einer einzigen Evolver-Sitzung aus."""
        logger.debug(f"Starting Evolver session with commands:\n{commands}")
        try:
            process = subprocess.Popen(
                [evolver_executable_path, self.input_file_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate(input=commands.encode(), timeout=timeout)
            if stderr:
                error_message = stderr.decode()
                logger.error(f"Error during Evolver session: {error_message}")
                raise RuntimeError(f"Evolver error: {error_message}")
            logger.debug(f"Evolver session output:\n{stdout.decode()}")
            return stdout.decode()
        except subprocess.TimeoutExpired:
            logger.error(f"Evolver session timed out after {timeout} seconds.")
            process.kill()
            raise
        except Exception as e:
            logger.exception(f"Exception during Evolver session: {e}")
            raise

    def optimize_surface(self):
        """Führt die Optimierungssequenz mit Logging und Fehlerüberprüfung durch."""
        logger.info("Starting optimization sequence.")
        try:
            commands = "\n".join(
                ["V" for _ in range(5)] +
                ["u" for _ in range(3)] +
                ["g 100"]
            )
            for cycle in range(10):
                logger.debug(f"Starting cycle {cycle + 1} of 10")
                self.run_evolver_session(commands)
            logger.info("Optimization sequence completed.")
        except Exception as e:
            logger.critical(f"Optimization aborted due to an error: {e}")
            raise

    def save_output(self):
        """Speichert das optimierte Modell im gewünschten Format."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{self.input_file_path[:-3]}_{timestamp}.off"

        try:
            if self.output_format == 'off':
                commands = f"""P
                                6
                                {output_file}
                                """
                self.run_evolver_session(commands)
                logger.info(f"Saved output as OFF file: {output_file}")
                print(f"Output saved to {output_file}")
            else:
                logger.warning(f"Unsupported output format: {self.output_format}")
                raise ValueError("Unsupported output format.")
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
