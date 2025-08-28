# predicates
airplanes = set()
airports = set()
cities = set()
trucks = set()
locations = set()
packages = set()

in_city = {}
at_location_init = {}
at_location_goal = {}

instance_path = "./instances/3-packages/p01.pddl"
with open() as f:
    content = f.read()

import re
PROBLEM_PATTERN = r"\(:init((?:\s*\([\w\s-]+\))+)\s*\)\s*\(:goal\s+\(and((?:\s*\([\w\s-]+\))+)\s*\)\s*\)"
AIRPLANE_PATTERN = r"\(AIRPLANE ([\w\d-]+)\)"
AIRPORT_PATTERN = r"\(AIRPORT ([\w\d-]+)\)"
CITY_PATTERN = r"\(CITY ([\w\d-]+)\)"
TRUCK_PATTERN = r"\(TRUCK ([\w\d-]+)\)"
LOCATION_PATTERN = r"\(LOCATION ([\w\d-]+)\)"
PACKAGE_PATTERN = r"\(OBJ ([\w\d-]+)\)"
IN_CITY_PATTERN = r"\(in-city ([\w\d-]+) ([\w\d-]+)\)"
AT_LOCATION_PATTERN = r"\(at ([\w\d-]+) ([\w\d-]+)\)"

problem_match = re.search(PROBLEM_PATTERN, content)
if not problem_match:
    raise ValueError(f"Problem not well defined for instance: {instance_path}")

initial_state_raw = problem_match.group(1)
goal_state_raw = problem_match.group(2)

for line in initial_state_raw.splitlines():
    line = line.strip()
    if match := re.match(AIRPLANE_PATTERN, line):
        airplanes.add(match.group(1))
    elif match := re.match(CITY_PATTERN, line):
        cities.add(match.group(1))
    elif match := re.match(TRUCK_PATTERN, line):
        trucks.add(match.group(1))
    elif match := re.match(LOCATION_PATTERN, line):
        locations.add(match.group(1))
    elif match := re.match(PACKAGE_PATTERN, line):
        packages.add(match.group(1))
    elif match := re.match(IN_CITY_PATTERN, line):
        in_city[match.group(1)] = match.group(2)
    elif match := re.match(AT_LOCATION_PATTERN, line):
        at_location_init[match.group(1)] = match.group(2)

for line in goal_state_raw.splitlines():
    line = line.strip()
    if match := re.match(AT_LOCATION_PATTERN, line):
        at_location_goal[match.group(1)] = match.group(2)

for p in packages:
    if p not in at_location_init:
        raise ValueError(f"Package {p} has no initial location defined.")
    
    if p not in at_location_goal:
        continue

    if at_location_init[p] == at_location_goal[p]:
        continue

    init_loc = at_location_init[p]
    goal_loc = at_location_goal[p]
    if init_loc not in locations:
        raise ValueError(f"Initial location {init_loc} for package {p} is not a valid location.")
    if goal_loc not in locations:
        raise ValueError(f"Goal location {goal_loc} for package {p} is not a valid location.")
    
    init_city = in_city.get(init_loc, None)
    goal_city = in_city.get(goal_loc, None)
    if init_city is None:
        raise ValueError(f"Initial location {init_loc} for package {p} has no associated city.")
    if goal_city is None:
        raise ValueError(f"Goal location {goal_loc} for package {p} has no associated city.")
    
    if init_city != goal_city:
        # must use the airplane
        # move truck to init_loc
        # load package into truck
        # move truck to location with airplane
        # unload package from truck

        # 