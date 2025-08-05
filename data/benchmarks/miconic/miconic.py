import subprocess
import os
import math
import numpy as np
"""
command: 
    ./ miconic 
        -f <num>    number of floors (minimal 2)
        -p <num>    number of passengers (minimal 1)
        -r <num>    random seed (optional)
output:
    instance file on stdout
"""

passenger = np.arange(4, 21, 4)
random_seed = np.arange(1, 5)
def floor(p):
    return 2 * p

# Create a directory for instances if it doesn't exist
script_dir = os.path.dirname(os.path.abspath(__file__))
instances_dir = os.path.join(script_dir, "instances")
os.makedirs(instances_dir, exist_ok=True)
miconic_path = os.path.join(script_dir, "miconic")

inst = 0
for p in range(len(passenger)):
    package_dir = os.path.join(instances_dir, f"{passenger[p]}-passenger")
    os.makedirs(package_dir, exist_ok=True)
    for r in range(len(random_seed)):
        inst += 1
        command = [
            miconic_path,
            "-f", str(floor(passenger[p])),
            "-p", str(passenger[p]),
            "-r", str(random_seed[r])
        ]
        instance_name = "p" + "0" * ((int(math.log10(len(random_seed) * len(passenger))) + 1) - (int(math.log10(inst) + 1))) + str(inst) + ".pddl"
        try:
            with open(os.path.join(package_dir, instance_name), "w") as instance_file:
                result = subprocess.run(command, capture_output=True, text=True)
                instance_file.write(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error executing logistics command: {e}")
            print(f"Error output: {e.stderr}")
