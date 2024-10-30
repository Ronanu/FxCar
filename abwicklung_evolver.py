import numpy as np
import tkinter as tk
from tkinter import filedialog
import os

def parse_off(file_path):
    """
    Function to parse an .off file and return vertices and faces.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Confirm the file starts with 'OFF' as expected for this format
    assert lines[0].strip() == 'OFF', "Not a valid OFF file"
    
    # Extract the header information with counts of vertices and faces
    counts = list(map(int, lines[1].strip().split()))
    num_vertices, num_faces = counts[0], counts[1]
    
    # Parse vertices
    vertices = [list(map(float, line.strip().split())) for line in lines[2:2 + num_vertices]]
    
    # Parse faces (assuming they are triangles)
    faces = [list(map(int, line.strip().split()[1:4])) for line in lines[2 + num_vertices:2 + num_vertices + num_faces]]
    
    return np.array(vertices), np.array(faces)

def ensure_cyclic_orientation(face, edge_map):
    """
    Ensures that edges of the given face follow a cyclic order to form a closed loop.
    """
    v1, v2, v3 = face
    ordered_edges = [
        edge_map[(v1, v2)],
        edge_map[(v2, v3)],
        edge_map[(v3, v1)]
    ]
    # Check if first and last vertices create a closed loop; otherwise, reorder
    if edge_map[(v1, v2)] != ordered_edges[0]:
        ordered_edges = ordered_edges[::-1]
    return ordered_edges

def generate_surface_evolver_file(vertices, faces, output_file_path):
    """
    Generate a Surface Evolver (.fe) file from vertices and faces with cyclically oriented facets.
    """
    with open(output_file_path, 'w') as fe_file:
        fe_file.write("// Surface Evolver datafile with cyclic facet orientation\n")
        fe_file.write("vertices\n")
        
        # Write vertices
        for i, (x, y, z) in enumerate(vertices, start=1):
            fe_file.write(f"{i} {x} {y} {z}\n")
        
        # Define edges explicitly
        fe_file.write("\nedges\n")
        edge_map = {}
        edge_id = 1
        for v1, v2, v3 in faces:
            edges = [(v1, v2), (v2, v3), (v3, v1)]
            for v_start, v_end in edges:
                if (v_start, v_end) not in edge_map and (v_end, v_start) not in edge_map:
                    fe_file.write(f"{edge_id} {v_start + 1} {v_end + 1}\n")
                    edge_map[(v_start, v_end)] = edge_id
                    edge_map[(v_end, v_start)] = edge_id  # Include reverse for orientation
                    edge_id += 1

        # Write faces with cyclic orientation
        fe_file.write("\nfaces\n")
        for i, face in enumerate(faces, start=1):
            face_edges = ensure_cyclic_orientation(face, edge_map)
            fe_file.write(f"{i} {face_edges[0]} {face_edges[1]} {face_edges[2]}\n")
        
        # Constraints to fix edges of the first triangle
        fe_file.write("\n// Constraints to fix edges for unfolding\n")
        fe_file.write("constraints\n")
        
        # Fix lengths of the first triangle's edges (edges between vertices of the first face)
        v1, v2, v3 = faces[0]
        fe_file.write(f"1 {{edge {edge_map[(v1, v2)]}}}\n")
        fe_file.write(f"2 {{edge {edge_map[(v2, v3)]}}}\n")
        fe_file.write(f"3 {{edge {edge_map[(v3, v1)]}}}\n")
        
        # Instructions for relaxation
        fe_file.write("\n// Instructions for relaxation\n")
        fe_file.write("gogo 1000\n")

# GUI for file selection and processing
def select_file_and_generate_fe():
    # Open file dialog to select .off file
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("OFF files", "*.off")])
    
    if not file_path:
        print("No file selected. Exiting.")
        return

    # Parse the OFF file
    vertices, faces = parse_off(file_path)
    
    # Define output path for the Surface Evolver file
    output_file_path = os.path.splitext(file_path)[0] + "_cyclic_oriented.fe"
    
    # Generate the Surface Evolver file with ordered and oriented facets and unfolding constraints
    generate_surface_evolver_file(vertices, faces, output_file_path)
    print(f"Surface Evolver file generated with cyclic facet orientation: {output_file_path}")

# Run the GUI and processing function
select_file_and_generate_fe()
