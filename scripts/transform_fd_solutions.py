import reasoning.settings  as settings

import os
domain = "blocksworld_backtrack"
def transform_fd_solutions_into_valid_plans(domain):
    domain_dir = os.path.join(settings.BENCHMARKS_DIR, domain)
    if not os.path.isdir(domain_dir):
        print(f"Missing domain directory for {domain}")
        return
    
    if not os.path.exists(os.path.join(domain_dir, "domain.pddl")):
        print(f"Missing domain file for {domain}")
        return
    
    solutions_dir = os.path.join(domain_dir, settings.SOLUTIONS_DIR_NAME)
    if not os.path.isdir(solutions_dir):
        print(f"Missing solutions directory for {domain}")
        return
    
    if not os.path.isdir(os.path.join(domain_dir, "instances")):
        print(f"Missing instances directory for {domain}")
        return

    for file in os.listdir(solutions_dir):
        instance_path = os.path.join(solutions_dir, file)
        # check dw instance
        if not instance_path.endswith(".pddl.soln.dw"):
            continue

        with open(instance_path, 'r') as f:
            content = f.read()
        
        reading = False
        lines = []
        for line in content.splitlines():
            if reading:
                if "Plan length" in line:
                    reading = False
                    break

                """
                Transform actions:
                unstack b2 b1 (1)
                ->
                (unstack b2 b1)
                """
                line = line.strip().split(" ")[:-1]
                line = " ".join(line)
                line = f"({line})"
                lines.append(line)

            if "Actual search time" in line:
                reading = True
        with open(instance_path.replace(".pddl.soln.dw", ".pddl.soln"), 'w') as f:
            f.write("\n".join(lines))

transform_fd_solutions_into_valid_plans(domain)