"""
command: 
    ./ blocksworld <ops> <num> <seed>
    -ops, between 3 and 4, inclusive
    -num, number of blocks (minimal 1, maximal 200)
    -seed, random seed (minimal 1)

output:
    instance file on stdout
"""

import subprocess
import os
import math
import numpy as np

# 5-10 : easy
# 11-15 : medium
# 16-20 : hard
random_seeds = np.arange(1, 3, dtype=int)

instances = {
    "5-to-10-blocks": {
        "blocks": np.arange(5, 10, dtype=int),
        "random_seeds": random_seeds
    },
    "10-to-15-blocks": {
        "blocks": np.arange(10, 15, dtype=int),
        "random_seeds": random_seeds
    },
    "15-to-20-blocks": {
        "blocks": np.arange(15, 20, dtype=int),
        "random_seeds": random_seeds
    },
    "20-to-25-blocks": {
        "blocks": np.arange(20, 25, dtype=int),
        "random_seeds": random_seeds
    }
}

script_dir = os.path.dirname(os.path.abspath(__file__))
instances_dir = os.path.join(script_dir, "instances")
os.makedirs(instances_dir, exist_ok=True)
blocksworld_path = os.path.join(script_dir, "blocksworld")

inst = 0
max_inst = sum(len(v["blocks"]) * len(v["random_seeds"]) for v in instances.values())
for inst_type, inst_data in instances.items():
    inst_dir = os.path.join(instances_dir, inst_type)
    os.makedirs(inst_dir, exist_ok=True)
    for b in inst_data["blocks"]:
        for s in inst_data["random_seeds"]:
            command = [blocksworld_path, "4", str(b), str(s)]
            inst += 1
            inst_name = "p" + "0" * ((int(math.log10(max_inst)) + 1) - (int(math.log10(inst)) + 1)) + str(inst) + ".pddl"
            try:
                with open(os.path.join(inst_dir, inst_name), "w") as instance_file:
                    result = subprocess.run(command, capture_output=True, text=True)
                    instance_file.write(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"Error executing blocksworld command: {e}")
                print(f"Error output: {e.stderr}")