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


blocks = [4, 6, 8, 10, 12]
random_seeds = [42, 57, 71, 84]

script_dir = os.path.dirname(os.path.abspath(__file__))
instances_dir = os.path.join(script_dir, "instances")
os.makedirs(instances_dir, exist_ok=True)
blocksworld_path = os.path.join(script_dir, "blocksworld")

for b in range(len(blocks)):
    blocks_dir = os.path.join(instances_dir, f"{blocks[b]}-blocks")
    os.makedirs(blocks_dir, exist_ok=True)
    for s in range(len(random_seeds)):
        command = [blocksworld_path, "4", str(blocks[b]), str(random_seeds[s])]
        inst = (len(random_seeds) * b) + s + 1
        instance_name = "p" + "0" * ((int(math.log10(len(blocks) * len(random_seeds))) + 1) - (int(math.log10(inst)) + 1)) + str(inst) + ".pddl"

        try:
            with open(os.path.join(blocks_dir, instance_name), "w") as instance_file:
                result = subprocess.run(command, capture_output=True, text=True)
                instance_file.write(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error executing blocksworld command: {e}")
            print(f"Error output: {e.stderr}")
