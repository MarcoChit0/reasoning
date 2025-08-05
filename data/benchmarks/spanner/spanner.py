import subprocess
import os
import math
import numpy as np
"""
command: 
    ./ python spanner-generator.py
        <num>    number of spanners (minimal 1) 
        <num>    number of nuts (minimal 1 and =< number of spanners)
        <num>    number of locations (minimal 1)
        --seed <num>    random seed (optional)
output:
    instance file on stdout
"""

spanners = np.arange(4, 21, 4)
random_seed = np.arange(1, 5)
def locations(s):
    return s + 1
def nuts(s):
    return s

# Create a directory for instances if it doesn't exist
script_dir = os.path.dirname(os.path.abspath(__file__))
instances_dir = os.path.join(script_dir, "instances")
os.makedirs(instances_dir, exist_ok=True)
spanner_generator_path = os.path.join(script_dir, "spanner-generator.py")

inst = 0
for p in range(len(spanners)):
    package_dir = os.path.join(instances_dir, f"{spanners[p]}-spanners")
    os.makedirs(package_dir, exist_ok=True)
    for r in range(len(random_seed)):
        inst += 1
        command = [
            "python",
            spanner_generator_path,
            str(spanners[p]),
            str(nuts(spanners[p])),
            str(locations(spanners[p])),
            "--seed", str(random_seed[r])
        ]
        instance_name = "p" + "0" * ((int(math.log10(len(random_seed) * len(spanners))) + 1) - (int(math.log10(inst) + 1))) + str(inst) + ".pddl"
        try:
            with open(os.path.join(package_dir, instance_name), "w") as instance_file:
                result = subprocess.run(command, capture_output=True, text=True)
                instance_file.write(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error executing logistics command: {e}")
            print(f"Error output: {e.stderr}")
