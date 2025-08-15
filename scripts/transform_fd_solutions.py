import reasoning.settings  as settings

import os
for domain in os.listdir(settings.SOLUTIONS_DIR):
    domain_dir = os.path.join(settings.SOLUTIONS_DIR, domain)
    if not os.path.isdir(domain_dir):
        continue 

    for instance in os.listdir(domain_dir):
        instance_path = os.path.join(domain_dir, instance)
        # check dw instance
        if not instance_path.endswith(".pddl.soln.dw"):
            continue
        # check already has instance
        if os.path.exists(instance_path.replace(".pddl.soln.dw", ".pddl.soln")):
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
