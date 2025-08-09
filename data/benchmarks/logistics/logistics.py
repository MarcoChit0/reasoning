import subprocess
import os
import math
import numpy as np
"""
command: 
    ./ logistics 
        -a <num>    number of airplanes
        -c <num>    number of cities (minimal 1)
        -s <num>    city size(minimal 1)
        -p <num>    number of packages (minimal 1)
        -t <num>    number of trucks (optional, default and minimal: same as number of cities; there will be at least one truck per city)
        -r <num>    random seed (minimal 1, optional)

output:
    instance file on stdout
"""

city = 3
location = 3 

airplane = 1
packages = np.arange(3, 18, 2)
random_seed = np.arange(1, 5)

# Create a directory for instances if it doesn't exist
script_dir = os.path.dirname(os.path.abspath(__file__))
instances_dir = os.path.join(script_dir, "instances")
os.makedirs(instances_dir, exist_ok=True)
logistics_path = os.path.join(script_dir, "logistics")

inst = 0
for p in range(len(packages)):
    package_dir = os.path.join(instances_dir, f"{packages[p]}-packages")
    os.makedirs(package_dir, exist_ok=True)
    for r in range(len(random_seed)):
        inst += 1
        command = [
            logistics_path,
            "-a", str(airplane),
            "-c", str(city),
            "-s", str(location),
            "-p", str(packages[p]),
            "-r", str(random_seed[r])
        ]
        instance_name = "p" + "0" * ((int(math.log10(len(random_seed) * len(packages))) + 1) - (int(math.log10(inst) + 1))) + str(inst) + ".pddl"
        try:
            with open(os.path.join(package_dir, instance_name), "w") as instance_file:
                result = subprocess.run(command, capture_output=True, text=True)
                instance_file.write(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error executing logistics command: {e}")
            print(f"Error output: {e.stderr}")
