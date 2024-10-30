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

def generate_surface_evolver_file_with_ordered_and_oriented_facets(vertices, faces, output_file_path):
    """
    Generate a Surface Evolver (.fe) file from vertices and faces with ordered and consistent facets.
    Fixes the first triangle's edges for the unfolding.
    """
    with open(output_file_path, 'w') as fe_file:
        # Write header information
        fe_file.write("// Surface Evolver datafile generated from .off file with ordered and oriented facets\n")
        fe_file.write("vertices\n")
        
        # Write vertices
        for i, (x, y, z) in enumerate(vertices, start=1):
            fe_file.write(f"{i} {x} {y} {z}\n")
        
        # Define edges explicitly with orientation consistency
        fe_file.write("\nedges\n")
        edge_map = {}
        edge_id = 1
        for v1, v2, v3 in faces:
            edges = [(v1, v2), (v2, v3), (v3, v1)]
            for v_start, v_end in edges:
                # Ensure each edge is only defined once, by storing both (v_start, v_end) and (v_end, v_start)
                if (v_start, v_end) not in edge_map and (v_end, v_start) not in edge_map:
                    fe_file.write(f"{edge_id} {v_start + 1} {v_end + 1}\n")
                    edge_map[(v_start, v_end)] = edge_id
                    edge_map[(v_end, v_start)] = edge_id  # Add reverse mapping for orientation consistency
                    edge_id += 1

        # Write faces (triangles) referencing edges in consistent cyclic order
        fe_file.write("\nfaces\n")
        for i, (v1, v2, v3) in enumerate(faces, start=1):
            # Ensure the edges are written in a consistent cyclic order
            face_edges = [edge_map[(v1, v2)], edge_map[(v2, v3)], edge_map[(v3, v1)]]
            if edge_map[(v1, v2)] != face_edges[0]:
                face_edges = face_edges[::-1]  # Reverse order to maintain cyclic orientation if necessary
            fe_file.write(f"{i} {face_edges[0]} {face_edges[1]} {face_edges[2]}\n")
        
        # Constraints section for fixing the first triangle edges
        fe_file.write("\n// Constraints to fix the edges of the first triangle\n")
        fe_file.write("constraints\n")
        
        # Fix lengths of the first triangle's edges (edges between vertices v1, v2, v3 of the first face)
        v1, v2, v3 = faces[0]
        fe_file.write(f"1 {{edge {edge_map[(v1, v2)]}}} // Fix edge length between vertices {v1+1} and {v2+1}\n")
        fe_file.write(f"2 {{edge {edge_map[(v2, v3)]}}} // Fix edge length between vertices {v2+1} and {v3+1}\n")
        fe_file.write(f"3 {{edge {edge_map[(v3, v1)]}}} // Fix edge length between vertices {v3+1} and {v1+1}\n")
        
        # Instructions for relaxation to achieve unfolding
        fe_file.write("\n// Instructions for relaxation\n")
        fe_file.write("gogo 1000 // Run relaxation steps to minimize energy and achieve unfolding\n")

# GUI for file selection and processing
def select_file_and_generate_fe_with_ordered_and_oriented_facets():
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
    output_file_path = os.path.splitext(file_path)[0] + "_oriented_facets.fe"
    
    # Generate the Surface Evolver file with ordered and oriented facets and unfolding constraints
    generate_surface_evolver_file_with_ordered_and_oriented_facets(vertices, faces, output_file_path)
    print(f"Surface Evolver file generated with ordered and oriented facets: {output_file_path}")

# Run the GUI and processing function
select_file_and_generate_fe_with_ordered_and_oriented_facets()
