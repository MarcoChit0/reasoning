import os
from reasoning.utils import val
import re

"""
pseudocode for solving any logistic problem:
for any package p that is not at the goal location:
    // different cities
    // must move p to the city which has the goal location
    if the goal location is not in the same city:
        // p's location do not have an airport
        // must move p to a location inside the city that has an airport
        if p's initial location has not an airport:
            move some truck t that is on the same city as p is to p's location 
            load p into t
            move t to the location that has an airport on the same city
            unload p from t
        // the airplane is not on the airport
        // must move an airplane to the airport and move p to the city which has the goal location
        if the airplane is not in the same city:
            move some airplane a that is in location from a different city than p is
            load p into a
            move a to the location that has an airport on the city which p goal's location is
            unload p from a
        // p ends at the same city such that its goal location is also in the same city
    // different locations
    // must move p to the goal location
    move some truck t that is on the same city as p is to p's location
    load p into t
    move t to the goal location
    unload p from t
    // p is now at the goal location
"""
def solve(instance_path):
    # patterns 
    PROBLEM_PATTERN = r"\(:init((?:\s*\([\w\s-]+\))+)\s*\)\s*\(:goal\s+\(and((?:\s*\([\w\s-]+\))+)\s*\)\s*\)"
    AIRPLANE_PATTERN = r"\(AIRPLANE\s+([\w\d-]+)\s*\)"
    AIRPORT_PATTERN = r"\(AIRPORT\s+([\w\d-]+)\s*\)"
    CITY_PATTERN = r"\(CITY\s+([\w\d-]+)\s*\)"
    TRUCK_PATTERN = r"\(TRUCK\s+([\w\d-]+)\s*\)"
    LOCATION_PATTERN = r"\(LOCATION\s+([\w\d-]+)\s*\)"
    PACKAGE_PATTERN = r"\(OBJ\s+([\w\d-]+)\s*\)"
    IN_CITY_PATTERN = r"\(in-city\s+([\w\d-]+)\s+([\w\d-]+)\s*\)"
    AT_LOCATION_PATTERN = r"\(at\s+([\w\d-]+)\s+([\w\d-]+)\s*\)"

    # predicates
    airplanes = set()
    airports = set()
    cities = set()
    trucks = set()
    locations = set()
    packages = set()
    plan = []
    in_city = {}

    # state
    current_location = {}
    goal_location = {}

    # helper functions
    def get_city(location):
        return in_city.get(location, None)

    def get_nearest_truck(package):
        # trucks in the same location
        for t in trucks:
            if current_location[t] == current_location[package]:
                return t

        # check for truck in the same city
        for t in trucks:
            if in_city.get(current_location[t]) == get_city(current_location[package]):
                return t

        # no truck found
        return None

    def get_nearest_airplane(package):
        # airplanes in the same location
        for a in airplanes:
            if current_location[a] == current_location[package]:
                return a
        
        # get any airplane
        if airplanes:
            return next(iter(airplanes))

        # no airplane found
        return None

    def get_nearest_airport(location):
        if location in airports:
            return location
        
        for a in airports:
            if in_city.get(a) == get_city(location):
                return a
        
        return None

    # read instance file
    with open(instance_path) as f:
        content = f.read()

    problem_match = re.search(PROBLEM_PATTERN, string=content)
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
            current_location[match.group(1)] = match.group(2)
        elif match := re.match(AIRPORT_PATTERN, line):
            airports.add(match.group(1))

    for line in goal_state_raw.splitlines():
        line = line.strip()
        if match := re.match(AT_LOCATION_PATTERN, line):
            goal_location[match.group(1)] = match.group(2)

    for p in packages:
        if p not in current_location:
            raise ValueError(f"Package {p} has no initial location defined.")

        if p not in goal_location or current_location[p] == goal_location[p]:
            continue

        if current_location[p] not in locations or goal_location[p] not in locations:
            raise ValueError(f"Missing init location {current_location[p]} or goal location {goal_location[p]} for package {p}")

        if get_city(location=current_location[p]) is None or get_city(location=goal_location[p]) is None:
            raise ValueError(f"Initial location {get_city(current_location[p])} or goal location {get_city(goal_location[p])} for package {p} has no associated city.")

        if get_city(current_location[p]) != get_city(goal_location[p]):
            airport_loc = get_nearest_airport(current_location[p])
            if airport_loc is None:
                raise ValueError(f"No airport found in city {get_city(current_location[p])} to move package {p} from location {current_location[p]}.")

            if airport_loc != current_location[p]:
                truck = get_nearest_truck(p)
                if truck is None:
                    raise ValueError(f"No truck found to move package {p} from location {current_location[p]}.")
                if current_location[truck] != current_location[p]:
                    plan.append(f"(DRIVE-TRUCK {truck} {current_location[truck]} {current_location[p]} {in_city[current_location[p]]})")
                    current_location[truck] = current_location[p]
                plan.append(f"(LOAD-TRUCK {p} {truck} {current_location[p]})")
                current_location[p] = None
                plan.append(f"(DRIVE-TRUCK {truck} {current_location[truck]} {airport_loc} {get_city(location=current_location[truck])})")
                current_location[truck] = airport_loc
                plan.append(f"(UNLOAD-TRUCK {p} {truck} {airport_loc})")
                current_location[p] = airport_loc
            
            airplane = get_nearest_airplane(p)
            if airplane is None:
                raise ValueError(f"No airplane found to move package {p} from location {current_location[p]} to city {get_city(goal_location[p])}.")
            if current_location[p] != current_location[airplane]:
                plan.append(f"(FLY-AIRPLANE {airplane} {current_location[airplane]} {airport_loc})")
                current_location[airplane] = airport_loc
            plan.append(f"(LOAD-AIRPLANE {p} {airplane} {airport_loc})")
            current_location[p] = None
            goal_airport = get_nearest_airport(goal_location[p])
            if goal_airport is None:
                raise ValueError(f"No airport found in city {get_city(goal_location[p])} to move package {p} to location {goal_location[p]}.")
            plan.append(f"(FLY-AIRPLANE {airplane} {airport_loc} {goal_airport})")
            current_location[airplane] = goal_airport
            plan.append(f"(UNLOAD-AIRPLANE {p} {airplane} {goal_airport})")
            current_location[p] = goal_airport

        if current_location[p] != goal_location[p]:
            truck = get_nearest_truck(p)
            if not truck:
                raise ValueError(f"No truck found to move package {p} from location {current_location[p]} to its goal location {goal_location[p]}.")
            if current_location[truck] != current_location[p]:
                plan.append(f"(DRIVE-TRUCK {truck} {current_location[truck]} {current_location[p]} {in_city[current_location[p]]})")
                current_location[truck] = current_location[p]
            plan.append(f"(LOAD-TRUCK {p} {truck} {current_location[p]})")
            current_location[p] = None
            plan.append(f"(DRIVE-TRUCK {truck} {current_location[truck]} {goal_location[p]} {get_city(location=current_location[truck])})")
            current_location[truck] = goal_location[p]
            plan.append(f"(UNLOAD-TRUCK {p} {truck} {goal_location[p]})")
            current_location[p] = goal_location[p]
    return plan


# --- Main execution logic ---
if __name__ == "__main__":
    correct = 0
    total = 0
    logistics_dir = os.path.dirname(os.path.abspath(__file__))
    domain = os.path.join(logistics_dir, "domain.pddl")
    instances_dir = os.path.join(logistics_dir, "instances")
    solutions_dir = os.path.join(logistics_dir, "solutions")
    if not os.path.exists(solutions_dir):
        os.makedirs(solutions_dir)
    if not os.path.exists(instances_dir):
        print(f"Error: Instances directory not found at '{instances_dir}'")
        print("Please create it and place your .pddl files inside.")
    else:
        for root, dirs, files in os.walk(instances_dir):
            for filename in files:
                if filename.endswith(".pddl"):
                    print(f"--- Solving: {filename} ---")
                    instance_path = os.path.join(root, filename)
                    total += 1
                    try:
                        plan = solve(instance_path)
                        solution_path = os.path.join(solutions_dir, filename + ".soln")
                        with open(solution_path, "w") as f:
                            f.write("\n".join(plan))
                        print(f"Solution saved to {solution_path}")
                        valid, error = val(domain, instance_path, solution_path, None)
                        if not valid:
                            raise ValueError(f"Validation failed for {filename}: {error}")
                        print(f"Validation successful for {filename}\n")
                        correct += 1
                    except ValueError as e:
                        raise e

    print(f"Total instances: {total}")
    print(f"Valid solutions: {correct}")
