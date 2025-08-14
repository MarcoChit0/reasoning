from reasoning.settings import SOLUTIONS_DIR, BENCHMARKS_DIR
import os 
from reasoning.utils import extract
from reasoning.task import Task, get_tasks
import subprocess

for domain in os.listdir(BENCHMARKS_DIR):
    domain_path = os.path.join(BENCHMARKS_DIR, domain)
    if not os.path.isdir(domain_path):
        continue
    tasks = get_tasks(domain)
    for task in tasks:
        path = os.path.join(SOLUTIONS_DIR, task.domain.name, task.instance.name + ".pddl.soln.rlx")
        if os.path.exists(path):
            continue
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        command = [
            "pyperplan",
            "-s", "gbf",
            "-H", "hffpo",
            task.domain.path,
            task.instance.path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Error running pyperplan for task {task}: {result.stderr}")

        relaxed_plan = extract(result.stdout, "relaxed_plan")
        if not relaxed_plan:
            raise RuntimeError(f"Failed to extract relaxed plan for task {task}")
        with open(path, "w") as f:
            f.write("<delete-relaxed-plan>\n")
            for action in relaxed_plan:
                f.write(f"{action}\n")
            f.write("</delete-relaxed-plan>\n")