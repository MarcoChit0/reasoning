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

# easy : 2 cities
# medium : 3 cities
# hard : 4 cities

instances = {
    "2-city-2-location": {
        "cities": 2,
        "locations": 2,
        "packages": np.arange(5, 15, dtype=int)
    },
    "3-city-3-location": {
        "cities": 3,
        "locations": 3,
        "packages": np.arange(5, 15, dtype=int)
    },
    "4-city-4-location": {
        "cities": 4,
        "locations": 4,
        "packages": np.arange(5, 15, dtype=int)
    },
    "5-city-5-location": {
        "cities": 5,
        "locations": 5,
        "packages": np.arange(5, 15, dtype=int)
    }
}

airplane = 1
random_seed = 42

# Create a directory for instances if it doesn't exist
script_dir = os.path.dirname(os.path.abspath(__file__))
instances_dir = os.path.join(script_dir, "instances")
os.makedirs(instances_dir, exist_ok=True)
logistics_path = os.path.join(script_dir, "logistics")

inst = 0
max_inst = sum(len(v["packages"]) for v in instances.values())
for inst_type, inst_data in instances.items():
    inst_dir = os.path.join(instances_dir, inst_type)
    os.makedirs(inst_dir, exist_ok=True)
    for p in inst_data["packages"]:
        inst += 1
        command = [
            logistics_path,
            "-a", str(airplane),
            "-c", str(inst_data["cities"]),
            "-s", str(inst_data["locations"]),
            "-p", str(p),
            "-r", str(random_seed)
        ]
        instance_name = "p" + "0" * ((int(math.log10(max_inst)) + 1) - (int(math.log10(inst) + 1))) + str(inst) + ".pddl"
        try:
            with open(os.path.join(inst_dir, instance_name), "w") as instance_file:
                result = subprocess.run(command, capture_output=True, text=True)
                instance_file.write(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error executing logistics command: {e}")
            print(f"Error output: {e.stderr}")