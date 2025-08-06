import subprocess
from reasoning.task import Task
"""
pyperplan -s astar -H actionlandmark ./data/raw/blocksworld/generated_domain.pddl ./data/raw/blocksworld/generated_basic/instance-1.pddl 
2025-07-28 15:42:30,514 INFO     using search: astar_search
2025-07-28 15:42:30,514 INFO     using heuristic: ActionLandmarkHeuristic
2025-07-28 15:42:30,514 INFO     Parsing Domain /home/macsilva/reasoning/data/raw/blocksworld/generated_domain.pddl
2025-07-28 15:42:30,515 INFO     Parsing Problem /home/macsilva/reasoning/data/raw/blocksworld/generated_basic/instance-1.pddl
2025-07-28 15:42:30,520 INFO     5 Predicates parsed
2025-07-28 15:42:30,520 INFO     4 Actions parsed
2025-07-28 15:42:30,520 INFO     3 Objects parsed
2025-07-28 15:42:30,520 INFO     0 Constants parsed
2025-07-28 15:42:30,520 INFO     Grounding start: bw-rand-3
2025-07-28 15:42:30,521 INFO     Relevance analysis removed 0 facts
2025-07-28 15:42:30,521 INFO     Grounding end: bw-rand-3
2025-07-28 15:42:30,521 INFO     19 Variables created
2025-07-28 15:42:30,521 INFO     24 Operators created
<landmarks-set>
(pick-up b)
(stack b a)
(unstack c b)
</landmarks-set>
"""

def get_action_landmarks(task : Task) -> list[str]:
    """
    Get action landmarks from a task using pyperplan.
    """
    
    command = [
        "pyperplan",
        "-s", "astar",
        "-H", "actionlandmark",
        task.domain.path,
        task.instance.path
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"Error running pyperplan: {result.stderr}")
    
    output = result.stdout
    start_index = output.find("<landmarks-set>")
    end_index = output.find("</landmarks-set>")
    
    if start_index == -1 or end_index == -1:
        raise ValueError("Action landmarks not found in the output.")

    action_landmarks_str = output[start_index + len("<landmarks-set>"):end_index].strip()
    action_landmarks = action_landmarks_str.splitlines()
    
    return [landmark.strip() for landmark in action_landmarks if landmark.strip()]

def call_val(domain_path : str, instance_path: str, plan_path : str) -> str:
    command = [
        f"res/val/build/bin/Validate",
        "-v",
        "-t", "0.001",
        domain_path,
        instance_path,
        plan_path
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error validating plan: {e.stderr.strip()}")

def from_config(config_path: str):
    """
    Load a configuration from a YAML file.
    """
    import yaml
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if not isinstance(config, dict):
        raise ValueError("Configuration file must contain a dictionary.")
    
    return config