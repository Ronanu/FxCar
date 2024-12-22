import subprocess
import os
import time
from datetime import datetime
import logging

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Absoluter Pfad zur Surface Evolver ausführbaren Datei
evolver_executable_path = r'C:\Evolver\evolver.exe'

class SurfaceEvolverAutomation:
    def __init__(self, input_file_path, output_format='OFF'):
        """Initialisiere mit Eingabedatei und gewünschtem Ausgabeformat."""
        self.input_file_path = os.path.abspath(input_file_path)
        self.output_format = output_format.lower()
        logger.info(f"Initialized for file: {self.input_file_path}, format: {output_format}")

    def diagnose_issues(self):
        """
        Validiert Eingabedateien und prüft, ob der Evolver korrekt installiert ist.
        """
        if not os.path.exists(evolver_executable_path):
            raise FileNotFoundError(f"Evolver executable not found: {evolver_executable_path}")
        if not os.path.exists(self.input_file_path):
            raise FileNotFoundError(f"Input file not found: {self.input_file_path}")
        if self.output_format not in ['off', 'stl']:
            raise ValueError(f"Unsupported output format: {self.output_format}")

    def start_evolver(self):
        """
        Startet den Surface Evolver als Subprozess mit weitergeleiteter Kommunikation.
        """
        process = subprocess.Popen(
            [evolver_executable_path, self.input_file_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        logger.info(f"Evolver started for file: {self.input_file_path}")
        return process

    def start_output_terminal(self):
        """
        Öffnet ein separates Terminal und gibt die Referenz zurück.
        """
        command = f'start cmd /k "echo Surface Evolver Communication && type con"'
        terminal = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            universal_newlines=True
        )
        logger.info("Output terminal opened.")
        return terminal

    def forward_to_terminal(self, process, terminal):
        """
        Leitet die Kommunikation des Evolvers ins Terminal weiter.
        """
        try:
            while process.poll() is None:  # Läuft der Prozess noch?
                output = process.stdout.readline()
                error = process.stderr.readline()
                if output:
                    terminal.stdin.write(output)
                    terminal.stdin.flush()
                if error:
                    terminal.stdin.write(f"ERROR: {error}")
                    terminal.stdin.flush()
        except Exception as e:
            logger.error(f"Error forwarding communication: {e}")

    def send_command(self, process, terminal, command):
        """Sendet einen Befehl an den Surface Evolver und zeigt ihn im Terminal."""
        try:
            process.stdin.write(f"{command}\n")
            process.stdin.flush()
            terminal.stdin.write(f"> {command}\n")
            terminal.stdin.flush()
        except Exception as e:
            logger.error(f"Failed to send command '{command}': {e}")
            raise

    def optimize_with_graphics(self, process, terminal):
        """
        Optimiert die Oberfläche mit grafischer Unterstützung.
        """
        try:
            print("Starting optimization. Press Enter to stop.")
            # Grafikanzeige starten
            self.send_command(process, terminal, "s")
            time.sleep(1)  # Warte, bis die Anzeige aktiv ist
            self.send_command(process, terminal, "x")

            # Optimierungsschleife
            while True:
                for command in ["V", "u", "g 100"]:
                    self.send_command(process, terminal, command)

                # Warten auf Benutzereingabe zum Abbrechen
                if input() == "":
                    logger.info("Optimization stopped by user.")
                    break
        except Exception as e:
            logger.error(f"Error during optimization: {e}")
        finally:
            process.terminate()

    def save_output(self, process, terminal):
        """
        Speichert die optimierte Oberfläche.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"{self.input_file_path[:-3]}_{timestamp}.off"
        try:
            for command in ["P", "6", output_file]:
                self.send_command(process, terminal, command)
            print(f"Output saved as: {output_file}")
        except Exception as e:
            logger.error(f"Error saving output: {e}")


if __name__ == "__main__":
    # Setze das Arbeitsverzeichnis
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Liste der Eingabedateien
    file_paths = ['surface_evolver_input.fe', 'surface_evolver_input.fe']

    for file_path in file_paths:
        evolver = SurfaceEvolverAutomation(file_path, output_format='OFF')
        try:
            evolver.diagnose_issues()
            process = evolver.start_evolver()
            terminal = evolver.start_output_terminal()

            # Kommunikation weiterleiten
            evolver.forward_to_terminal(process, terminal)

            # Optimierung starten
            evolver.optimize_with_graphics(process, terminal)

            # Datei speichern
            evolver.save_output(process, terminal)
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            break
