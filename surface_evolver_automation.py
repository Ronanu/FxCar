import subprocess
import os
import time
import threading
import tkinter as tk
from tkinter import scrolledtext
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
    def __init__(self, input_file_path, output_format='OFF', gui=None):
        """Initialisiere mit Eingabedatei, gewünschtem Ausgabeformat und GUI-Referenz."""
        self.input_file_path = os.path.abspath(input_file_path)
        self.output_format = output_format.lower()
        self.gui = gui  # Tkinter GUI-Referenz
        self.process = None
        self.optimization_running = False  # Optimierungsstatus
        logger.info(f"Initialized for file: {self.input_file_path}, format: {output_format}")

    def diagnose_issues(self):
        """Validiert Eingabedateien und prüft, ob der Evolver korrekt installiert ist."""
        if not os.path.exists(evolver_executable_path):
            raise FileNotFoundError(f"Evolver executable not found: {evolver_executable_path}")
        if not os.path.exists(self.input_file_path):
            raise FileNotFoundError(f"Input file not found: {self.input_file_path}")
        if self.output_format not in ['off', 'stl']:
            raise ValueError(f"Unsupported output format: {self.output_format}")

    def start_evolver(self):
        """Startet den Surface Evolver als Subprozess."""
        self.process = subprocess.Popen(
            [evolver_executable_path, self.input_file_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        logger.info(f"Evolver started for file: {self.input_file_path}")
        return self.process

    def forward_output_to_gui(self):
        """Leitet die Ausgaben und Fehler des Surface Evolvers live an das Tkinter-Textfeld weiter."""
        try:
            while self.process.poll() is None:  # Solange der Prozess läuft
                output = self.process.stdout.readline()
                error = self.process.stderr.readline()
                if output.strip():
                    self.gui.append_output(output)
                if error.strip():
                    self.gui.append_output(f"ERROR: {error}")
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error forwarding communication: {e}")

    def send_command(self, command):
        """Sendet einen Befehl an den Surface Evolver."""
        try:
            self.process.stdin.write(f"{command}\n")
            self.process.stdin.flush()
            if self.gui:
                self.gui.append_output(f"> {command}")
        except Exception as e:
            logger.error(f"Failed to send command '{command}': {e}")
            raise

    def open_graphics(self):
        """Öffnet die grafische Anzeige des Evolvers."""
        try:
            self.send_command("s")
            time.sleep(1)  # Warte, bis die Anzeige aktiv ist
            self.send_command("x")  # Zurück in den Editor, ohne die Anzeige zu schließen
            self.gui.append_output("Graphics window opened.")
        except Exception as e:
            logger.error(f"Error opening graphics: {e}")

    def optimize(self):
        """Führt die Optimierungslogik aus."""
        try:
            while self.optimization_running:
                for command in ["V", "u", "g 100"]:
                    if not self.optimization_running:
                        break  # Falls während eines Durchlaufs pausiert wurde
                    self.send_command(command)
                    time.sleep(0.5)  # Wartezeit für Synchronisation
        except Exception as e:
            logger.error(f"Error during optimization: {e}")
        finally:
            self.gui.append_output("Optimization stopped.")

    def save_output(self):
        """Speichert die optimierte Oberfläche."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"{self.input_file_path[:-3]}_{timestamp}.off"
        try:
            for command in ["P", "6", output_file]:
                self.send_command(command)
            self.gui.append_output(f"Output saved as: {output_file}")
        except Exception as e:
            logger.error(f"Error saving output: {e}")


class EvolverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Surface Evolver GUI")

        # Textfeld für die Ausgabe
        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20, width=80)
        self.output_text.pack(pady=10)

        # Buttons
        self.control_frame = tk.Frame(root)
        self.control_frame.pack()

        self.open_graphics_button = tk.Button(self.control_frame, text="Open Graphics", command=self.open_graphics)
        self.open_graphics_button.pack(side=tk.LEFT, padx=5)

        self.start_button = tk.Button(self.control_frame, text="Start Optimization", command=self.start_optimization)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.pause_button = tk.Button(self.control_frame, text="Pause Optimization", command=self.pause_optimization)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        self.continue_button = tk.Button(self.control_frame, text="Continue Optimization", command=self.continue_optimization)
        self.continue_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(self.control_frame, text="Save Output", command=self.save_output)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.evolver = None  # Referenz zur Evolver-Instanz

    def append_output(self, text):
        """Fügt Text in das Ausgabefeld ein."""
        self.output_text.insert(tk.END, f"{text}\n")
        self.output_text.see(tk.END)

    def start_evolver(self, file_path):
        """Startet den Evolver-Prozess."""
        self.append_output("Starting Surface Evolver...")
        self.evolver = SurfaceEvolverAutomation(file_path, gui=self)
        self.evolver.diagnose_issues()
        process = self.evolver.start_evolver()

        # Starte einen Thread für die Ausgabe
        threading.Thread(target=self.evolver.forward_output_to_gui, daemon=True).start()

    def open_graphics(self):
        """Öffnet die grafische Anzeige."""
        if self.evolver:
            self.evolver.open_graphics()

    def start_optimization(self):
        """Startet die Optimierung."""
        if self.evolver:
            self.evolver.optimization_running = True
            self.append_output("Optimization started.")
            threading.Thread(target=self.evolver.optimize, daemon=True).start()

    def pause_optimization(self):
        """Pausiert die Optimierung."""
        if self.evolver:
            self.evolver.optimization_running = False
            self.append_output("Optimization paused.")

    def continue_optimization(self):
        """Setzt die Optimierung fort."""
        if self.evolver:
            self.evolver.optimization_running = True
            self.append_output("Optimization continued.")
            threading.Thread(target=self.evolver.optimize, daemon=True).start()

    def save_output(self):
        """Speichert die optimierte Datei."""
        if self.evolver:
            self.evolver.save_output()


if __name__ == "__main__":
    # Tkinter-Setup
    root = tk.Tk()
    gui = EvolverGUI(root)
    threading.Thread(target=lambda: gui.start_evolver("surface_evolver_input.fe"), daemon=True).start()
    root.mainloop()