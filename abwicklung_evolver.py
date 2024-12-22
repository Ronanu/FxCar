import numpy as np
import tkinter as tk
from tkinter import filedialog
import os

def parse_off(file_path):
    """
    Funktion zum Parsen einer .off-Datei und Rückgabe von Vertices und Faces.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Überprüfen, ob die Datei mit 'OFF' beginnt
    assert lines[0].strip() == 'OFF', "Keine gültige OFF-Datei"
    
    # Extrahieren der Anzahl von Vertices und Faces
    counts = list(map(int, lines[1].strip().split()))
    num_vertices, num_faces = counts[0], counts[1]
    
    # Parsen der Vertices
    vertices = [list(map(float, line.strip().split())) for line in lines[2:2 + num_vertices]]
    
    # Parsen der Faces (angenommen, sie sind Dreiecke)
    faces = [list(map(int, line.strip().split()[1:4])) for line in lines[2 + num_vertices:2 + num_vertices + num_faces]]
    
    return np.array(vertices), np.array(faces)

def generate_surface_evolver_file(vertices, faces, output_file_path):
    """
    Generiert eine Surface Evolver (.fe)-Datei aus Vertices und Faces mit konsistenter Kantenorientierung.
    """
    with open(output_file_path, 'w') as fe_file:
        # Header-Informationen schreiben
        fe_file.write("// Surface Evolver Datenfile mit konsistenter Kantenorientierung\n")
        fe_file.write("vertices\n")
        
        # Schreiben der Vertices
        for i, (x, y, z) in enumerate(vertices, start=1):
            fe_file.write(f"{i} {x} {y} {z}\n")
        
        # Definieren der Kanten mit konsistenter Orientierung
        fe_file.write("\nedges\n")
        edge_map = {}
        edge_id = 1
        for v1, v2, v3 in faces:
            edges = [(v1, v2), (v2, v3), (v3, v1)]
            for v_start, v_end in edges:
                if (v_start, v_end) not in edge_map and (v_end, v_start) not in edge_map:
                    fe_file.write(f"{edge_id} {v_start + 1} {v_end + 1}\n")
                    edge_map[(v_start, v_end)] = edge_id
                    edge_map[(v_end, v_start)] = -edge_id  # Umgekehrte Orientierung
                    edge_id += 1

        # Schreiben der Faces mit korrekt orientierten Kanten
        fe_file.write("\nfaces\n")
        for i, (v1, v2, v3) in enumerate(faces, start=1):
            face_edges = [edge_map[(v1, v2)], edge_map[(v2, v3)], edge_map[(v3, v1)]]
            fe_file.write(f"{i} {' '.join(map(str, face_edges))}\n")

def select_file_and_generate_fe():
    """
    Öffnet einen Dateidialog zur Auswahl einer .off-Datei und generiert die entsprechende .fe-Datei.
    """
    # Öffnen des Dateidialogs zur Auswahl der .off-Datei
    root = tk.Tk()
    root.withdraw()  # Versteckt das Hauptfenster
    file_path = filedialog.askopenfilename(filetypes=[("OFF-Dateien", "*.off")])
    
    if not file_path:
        print("Keine Datei ausgewählt. Beende.")
        return

    # Parsen der OFF-Datei
    vertices, faces = parse_off(file_path)
    
    # Definieren des Ausgabewegs für die Surface Evolver-Datei
    output_file_path = os.path.splitext(file_path)[0] + "_oriented.fe"
    
    # Generieren der Surface Evolver-Datei mit konsistenter Kantenorientierung
    generate_surface_evolver_file(vertices, faces, output_file_path)
    print(f"Surface Evolver-Datei erfolgreich generiert: {output_file_path}")

# Ausführen der GUI und der Verarbeitungsfunktion
if __name__ == "__main__":
    select_file_and_generate_fe()
