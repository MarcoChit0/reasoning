import sys
import os
import re
from reasoning.utils import val

def solve(instance_path):
    # return a non-optimal plan for a blocksworld task.

    # unstack each block 
    # put-down each block
    # pick-up each block
    # stack each block

    plan = []
    # This regex is updated to be more specific about the content of the init and goal blocks.
    # It now explicitly matches sequences of parenthesized facts, avoiding the ambiguity of the previous version.
    problem_regex = r"\(:init((?:\s*\([\w\s-]+\))+)\s*\)\s*\(:goal\s+\(and((?:\s*\([\w\s-]+\))+)\s*\)\s*\)"

    on_regex = r"\(on\s+([\w-]+)\s+([\w-]+)\)"
    on_table_regex = r"\(on-table\s+([\w-]+)\)"
    clear_regex = r"\(clear\s+([\w-]+)\)"
    holding_regex = r"\(holding\s+([\w-]+)\)"

    with open(instance_path, 'r') as f:
        content = f.read()

    # Extract initial state
    # The new regex is more robust and doesn't rely on broad flags like DOTALL.
    problem_match = re.search(problem_regex, content)
    if not problem_match:
        raise ValueError(f"Problem not well defined for: {instance_path}")

    initial_state_raw = problem_match.group(1)
    goal_state_raw = problem_match.group(2)

    initial_state = [line.strip() for line in initial_state_raw.strip().splitlines() if line.strip()]
    goal_state = [line.strip() for line in goal_state_raw.strip().splitlines() if line.strip()]


    init_mapping = {}
    # A
    # B
    # -
    # on(A, B) -> map_over[B] = A
    # on-table(B) -> map_over["table"] = [B]
    for line in initial_state:
        if match := re.search(on_regex, line):
            init_mapping[match.group(2)] = match.group(1)
        elif match := re.search(on_table_regex, line):
            if "table" in init_mapping:
                init_mapping["table"].append(match.group(1))
            else:
                init_mapping["table"] = [match.group(1)]
        elif match := re.search(holding_regex, line):
            if "hand" in init_mapping:
                raise ValueError(f"Invalid state: holding more than one block for instance: {instance_path}")
            init_mapping["hand"] = match.group(1)
        elif line == "(arm-empty)":
            init_mapping["hand"] = None
    
    goal_mapping_forward = {}
    goal_mapping_backward = {}
    for line in goal_state:
        if match := re.search(on_regex, line):
            goal_mapping_forward[match.group(2)] = match.group(1)
            goal_mapping_backward[match.group(1)] = match.group(2)
        elif match := re.search(on_table_regex, line):
            if "table" in goal_mapping_forward:
                goal_mapping_forward["table"].append(match.group(1))
            else:
                goal_mapping_forward["table"] = [match.group(1)]
            goal_mapping_backward[match.group(1)] = "table"
        elif match := re.search(holding_regex, line):
            if "hand" in goal_mapping_forward:
                raise ValueError(f"Invalid state: holding more than one block for instance: {instance_path}")
            goal_mapping_forward["hand"] = match.group(1)
            goal_mapping_backward[match.group(1)] = "hand"
        elif line == "(arm-empty)":
            goal_mapping_forward["hand"] = None


    blocks = set()
    for block in init_mapping["table"]:
        stack = []
        b = block
        while True:
            stack.append(b)
            blocks.add(b)
            if b in init_mapping and init_mapping[b] != b: 
                b = init_mapping[b]
            else:
                break
        if len(stack) > 1:
            for i in range(len(stack)-1, 0, -1):
                top_block = stack[i]
                bottom_block = stack[i-1]
                plan.append(f"(unstack {top_block} {bottom_block})")
                plan.append(f"(putdown {top_block})")

    # NOTE: Not all blocks are cited on the goal
    in_goal = set()
    for block in blocks:
        if in_goal.__contains__(block):
            continue
        cur = block
        stack = []
        while cur in goal_mapping_backward and goal_mapping_backward[cur] != "table":
            cur = goal_mapping_backward[cur]
        
        while cur is not None:
            stack.append(cur)
            in_goal.add(cur)
            cur = goal_mapping_forward.get(cur, None)
        
        if len(stack) > 1:
            for i in range(1, len(stack), 1):
                bottom_block = stack[i-1]
                top_block = stack[i]
                plan.append(f"(pickup {top_block})")
                plan.append(f"(stack {top_block} {bottom_block})")

    return plan

# --- Main execution logic ---
if __name__ == "__main__":
    correct = 0
    total = 0
    blocksworld_dir = os.path.dirname(os.path.abspath(__file__))
    domain = os.path.join(blocksworld_dir, "domain.pddl")
    instances_dir = os.path.join(blocksworld_dir, "instances")
    solutions_dir = os.path.join(blocksworld_dir, "solutions")
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
