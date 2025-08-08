"""
command: 
    python generator.py <grid_size> <conf_blocks>
	 line numbers is used for defining number of lines of the screen.
	 The number of column is fixed at 4. E.g., 8-> 8x4 grid. Only odd numbers accepted.
	 conf_blocks:
		 1 -> only 1x1 square blocks
		 2 -> only 2x1 blocks
		 3 -> only L-shaped blocks
		 4 -> mix of blocks

output:
    instance file on stdout
"""

import subprocess
import os
import math
import numpy as np

grid_sizes = np.arange(4, 13, 2)
random_seeds = np.arange(1, 5)
conf_blocks = 4

script_dir = os.path.dirname(os.path.abspath(__file__))
instances_dir = os.path.join(script_dir, "instances")
os.makedirs(instances_dir, exist_ok=True)
tetris_path = os.path.join(script_dir, "generator.py")

inst = 0
for g in range(len(grid_sizes)):
    grid_dir = os.path.join(instances_dir, f"{grid_sizes[g]}-grid")
    os.makedirs(grid_dir, exist_ok=True)
    for s in range(len(random_seeds)):
        command = ["python", tetris_path, str(grid_sizes[g]), str(conf_blocks)]
        inst += 1
        instance_name = f"p{inst:02}.pddl"

        try:
            with open(os.path.join(grid_dir, instance_name), "w") as instance_file:
                result = subprocess.run(command, capture_output=True, text=True)
                instance_file.write(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error executing tetris command: {e}")
            print(f"Error output: {e.stderr}")
