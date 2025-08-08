import subprocess
import os
import math
import numpy as np

# Command: python minigrid-generator.py <floorplan_name> <shape> --seed <random_seed> --floorplans_path <floorplans_path> --results <results_path>
# Output: file on the results path that starts with grid_
shapes = np.arange(1, 6, 1)
random_seed = np.arange(1, 5)

# Create a directory for instances if it doesn't exist
script_dir = os.path.dirname(os.path.abspath(__file__))
instances_dir = os.path.join(script_dir, "instances")
floorplans_dir = os.path.join(script_dir, "floorplans")
os.makedirs(instances_dir, exist_ok=True)
os.makedirs(floorplans_dir, exist_ok=True)
minigrid_path = os.path.join(script_dir, "minigrid-generator.py")

inst = 0
for s in range(len(shapes)):
    shape_dir = os.path.join(instances_dir, f"{shapes[s]}-shape")
    os.makedirs(shape_dir, exist_ok=True)
    for r in range(len(random_seed)):
        inst += 1
        instance_name = f"p{inst:02}.pddl"
        floorplan_name = "4room2.fpl"
            
        command = [
            "python",
            minigrid_path,
            floorplan_name,
            str(shapes[s]),
            "--seed", str(random_seed[r]),
            "--floorplans_path", floorplans_dir,
            "--results", shape_dir
        ]
        
        _ = subprocess.run(command, check=True, capture_output=True, text=True)
        files = os.listdir(shape_dir)
        found = False
        for f in files:
            if f.startswith("grid_"):
                os.rename(os.path.join(shape_dir, f), os.path.join(shape_dir, instance_name))
                found = True
                break
        if not found:
            raise FileNotFoundError(f"No grid file found for instance {instance_name} in {shape_dir}")
        
