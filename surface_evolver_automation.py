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

evolver_executable_path = r'C:\Evolver\evolver.exe'


class SurfaceEvolverAutomation:
    def __init__(self, input_file_path, output_format='OFF', gui=None):
        """Initialisiere mit Eingabedatei, gewünschtem Ausgabeformat und GUI-Referenz."""
        self.input_file_path = os.path.abspath(input_file_path)
        self.output_format = output_format.lower()
        self.gui = gui
        self.process = None
        self.optimization_running = False
        logger.info(f"Initialized for file: {self.input_file_path}, format: {output_format}")

    def diagnose_issues(self):
        """Prüfe Dateien und Programmumgebung."""
        if not os.path.exists(evolver_executable_path):
            raise FileNotFoundError(f"Evolver executable not found: {evolver_executable_path}")
        if not os.path.exists(self.input_file_path):
            raise FileNotFoundError(f"Input file not found: {self.input_file_path}")
        if self.output_format not in ['off', 'stl']:
            raise ValueError(f"Unsupported output format: {self.output_format}")

    def start_evolver(self):
        """Starte den Surface Evolver."""
        self.process = subprocess.Popen(
            [evolver_executable_path, self.input_file_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1,
            universal_newlines=True
        )
        logger.info(f"Evolver started for file: {self.input_file_path}")
        return self.process

    def forward_output_to_gui(self):
        """Leite Ausgaben des Evolvers an die GUI weiter."""
        try:
            while self.process.poll() is None:
                output = self.process.stdout.readline()
                if output.strip():
                    self.gui.append_output(output.strip())
                error = self.process.stderr.readline()
                if error.strip():
                    self.gui.append_output(f"ERROR: {error.strip()}")
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error forwarding output: {e}")

    def send_command(self, command):
        """Sende einen Befehl an den Surface Evolver, ohne auf Feedback zu warten."""
        try:
            self.process.stdin.write(f"{command}\n")
            self.process.stdin.flush()
            if self.gui:
                self.gui.append_output(f"> {command}")
        except Exception as e:
            logger.error(f"Failed to send command '{command}': {e}")
            raise

    def send_command_and_wait(self, command, expected_feedback_count=1, timeout=10):
        """
        Sende einen Befehl an den Surface Evolver und warte auf eine festgelegte Anzahl von Rückmeldungen.
        
        :param command: Der zu sendende Befehl.
        :param expected_feedback_count: Anzahl der erwarteten Rückmeldungen.
        :param timeout: Maximale Wartezeit für jede Rückmeldung (in Sekunden).
        """
        try:
            self.process.stdin.write(f"{command}\n")
            self.process.stdin.flush()
            if self.gui:
                self.gui.append_output(f"> {command}")

            # Warte auf die Rückmeldungen
            received_feedback = 0
            start_time = time.time()

            while received_feedback < expected_feedback_count:
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"No response from Evolver for command: {command}")
                output = self.process.stdout.readline()
                if output.strip():
                    received_feedback += 1
                    if self.gui:
                        self.gui.append_output(output.strip())
        except Exception as e:
            logger.error(f"Failed to send command '{command}' or wait for response: {e}")
            raise

    def open_graphics(self):
        """Öffnet die grafische Anzeige."""
        self.send_command("s")
        self.send_command("x")
        self.gui.append_output("Graphics window opened.")

    def optimize(self):
        """Führt die Optimierung durch."""
        try:
            while self.optimization_running:
                for command, feedback_count in [("V", 1), ("u", 1), ("g 50", 50)]:
                    if not self.optimization_running:
                        break
                    if command == 'V' or command == 'u':
                        for _ in range(10):
                            self.send_command_and_wait(command, expected_feedback_count=feedback_count)
                    else:
                        self.send_command_and_wait(command, expected_feedback_count=feedback_count)
        except Exception as e:
            logger.error(f"Error during optimization: {e}")
        finally:
            self.gui.append_output("Optimization stopped.")

    def save_output(self):
        """Speichert die optimierte Datei."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"{self.input_file_path[:-3]}_{timestamp}.off"
        try:
            for command in ["P", "6", output_file]:
                self.send_command_and_wait(command)
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

        self.save_button = tk.Button(self.control_frame, text="Save Output", command=self.save_output)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.evolver = None

    def append_output(self, text):
        """Fügt Text in das Ausgabefeld ein."""
        def safe_insert():
            self.output_text.insert(tk.END, f"{text}\n")
            self.output_text.see(tk.END)

        self.root.after(0, safe_insert)

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

    def save_output(self):
        """Speichert die optimierte Datei."""
        if self.evolver:
            self.evolver.save_output()


if __name__ == "__main__":
    root = tk.Tk()
    gui = EvolverGUI(root)
    threading.Thread(target=lambda: gui.start_evolver("surface_evolver_input.fe"), daemon=True).start()
    root.mainloop()