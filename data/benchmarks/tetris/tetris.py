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
conf_blocks = 4

script_dir = os.path.dirname(os.path.abspath(__file__))
instances_dir = os.path.join(script_dir, "instances")
os.makedirs(instances_dir, exist_ok=True)
tetris_path = os.path.join(script_dir, "generator.py")

inst = 1
for g in range(len(grid_sizes)):
    grid_dir = os.path.join(instances_dir, f"{grid_sizes[g]}-grid")
    os.makedirs(grid_dir, exist_ok=True)
    created_instances = 0
    seed = 0
    
    while created_instances < 4:
        seed += 1
        command = ["python", tetris_path, str(grid_sizes[g]), str(conf_blocks), str(seed)]
        instance_name = f"p{inst:02}.pddl"
        instance_path = os.path.join(grid_dir, instance_name)
        solution_path = instance_path + ".soln"
        
        try:
            # Generate tetris instance
            with open(instance_path, "w") as instance_file:
                result = subprocess.run(command, capture_output=True, text=True)
                instance_file.write(result.stdout)
            
            # Try to solve with pyperplan
            pyperplan_cmd = [
                "./res/pyperplan/pyperplan",
                "-s", "gbf",
                "-H", "lmcut",
                "data/benchmarks/tetris/domain.pddl",
                instance_path,
            ]
            
            # Run pyperplan with timeout
            subprocess.run(pyperplan_cmd, timeout=300, check=False)
            
            # Check if solution file exists
            if os.path.exists(solution_path):
                print(f"Solution found for instance {instance_name} with seed {seed}")
                created_instances += 1
                inst += 1
            else:
                print(f"No solution found for instance {instance_name} with seed {seed}")
                os.remove(instance_path)
        
        except Exception as e:
            print(f"Error processing instance {instance_name}: {e}")
            if os.path.exists(instance_path):
                os.remove(instance_path)
