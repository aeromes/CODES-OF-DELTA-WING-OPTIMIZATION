import time
import gmsh
import os
import numpy as np
import pandas as pd
import math
import sys

output_folder = sys.argv[1]
base_folder = os.path.dirname(output_folder)
valid_path = output_folder + "/samples.csv"
geometries_path =os.path.join(output_folder, "geometries")
os.chdir(output_folder)
df = pd.read_csv(valid_path)

gmsh.initialize()
mesh_sizes = [0.01]

for index in range(len(df)):
    for meshsizemin in mesh_sizes:
        sweep_ang = df.iat[index,1]
        b = df.iat[index,2]/2
        leading_edge= b/math.cos(math.radians(sweep_ang))
        n=leading_edge/meshsizemin
        n_other=b/meshsizemin
        start=time.time()
        gmsh.model.add("OpenCASCADE")
        gmsh.model.occ.importShapes(os.path.join(geometries_path,f"Delta_Wing_Geometry_{index + 1}.step"))

        gmsh.model.occ.addSphere(0, 0, 0, 50, 2)
        gmsh.model.occ.addBox(50, 0, 50, -100, -50, -100, 3)

        gmsh.model.occ.cut([(3, 2)], [(3, 3)], 4)
        gmsh.model.occ.cut([(3, 4)], [(3, 1)], 5)

        gmsh.model.occ.synchronize()

        gmsh.model.addPhysicalGroup(2, [1], name="FARFIELD")
        gmsh.model.addPhysicalGroup(2, [3, 4, 5, 6, 7], name="WING")
        gmsh.model.addPhysicalGroup(3, [5], name="VOLUME")
        gmsh.model.addPhysicalGroup(2, [2], name="SYMMETRY")

        dist_field = gmsh.model.mesh.field.add("Distance")
        gmsh.model.mesh.field.setNumbers(dist_field, "PointsList", [5, 6, 7, 8, 9, 10, 11, 12])
        gmsh.model.mesh.field.setNumbers(dist_field, "CurvesList", [11,15,17])
        gmsh.model.mesh.setTransfiniteCurve(13, int(n))
        gmsh.model.mesh.setTransfiniteCurve(15, int((n_other+n)/2))
        gmsh.model.mesh.setTransfiniteCurve(11, int((n_other+n)/2))

        thr_field = gmsh.model.mesh.field.add("Threshold")
        gmsh.model.mesh.field.setNumber(thr_field, "InField", dist_field)

        gmsh.model.mesh.field.setNumber(thr_field, "SizeMin", meshsizemin)
        gmsh.model.mesh.field.setNumber(thr_field, "SizeMax", 2.0)
        gmsh.model.mesh.field.setNumber(thr_field, "DistMin", 0.0)
        gmsh.model.mesh.field.setNumber(thr_field, "DistMax", 20.0)
        gmsh.model.mesh.field.setAsBackgroundMesh(thr_field)
        gmsh.option.setNumber("Mesh.AngleToleranceFacetOverlap", 0.001)
        gmsh.model.mesh.generate(3)
        sample_name = f"sample_{index+1}"
        folder_path = os.path.join(os.getcwd(), sample_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        mesh_file_name = f"mesh_{sample_name}.su2"
        mesh_file_path = os.path.join(folder_path, mesh_file_name)
        gmsh.write(mesh_file_path)

gmsh.finalize()