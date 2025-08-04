import subprocess
import os
import math

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

cities = [2, 3]
locations = [1, 2]

airplane = 1
packages = [5, 6, 7, 8, 9]
random_seed = 42

# Create a directory for instances if it doesn't exist
script_dir = os.path.dirname(os.path.abspath(__file__))
instances_dir = os.path.join(script_dir, "instances")
os.makedirs(instances_dir, exist_ok=True)
logistics_path = os.path.join(script_dir, "logistics")

for c in range(len(cities)):
    city_dir = os.path.join(instances_dir, f"{cities[c]}-city")
    os.makedirs(city_dir, exist_ok=True)

    for l in range(len(locations)):
        location_dir = os.path.join(city_dir, f"{locations[l]}-location")
        os.makedirs(location_dir, exist_ok=True)

        for p in range(len(packages)):
            inst = (len(packages)*len(locations)*c) + (len(packages)*l) + p + 1
            
            command = [
                logistics_path,
                "-a", str(airplane),
                "-c", str(cities[c]),
                "-s", str(locations[l]),
                "-p", str(packages[p]),
                "-r", str(random_seed)
            ]

            instance_name = "p" + "0" * ((int(math.log10(len(cities) * len(locations) * len(packages))) + 1) - (int(math.log10(inst) + 1))) + str(inst) + ".pddl"

            try:
                with open(os.path.join(location_dir, instance_name), "w") as instance_file:
                    result = subprocess.run(command, capture_output=True, text=True)
                    instance_file.write(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"Error executing logistics command: {e}")
                print(f"Error output: {e.stderr}")
