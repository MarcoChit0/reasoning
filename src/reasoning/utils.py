import subprocess

from typing import Optional
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
<action-landmarks-set>
(pick-up b)
(stack b a)
(unstack c b)
</action-landmarks-set>
"""
import os
def from_pyperplan(task: Task, obj: str) -> None | str | list[str]:
    """
    Get a specific object from the pyperplan output for a task.
    """
    if obj == "landmark":
        extension = ".pddl.lndmk"
        command = [
            "pyperplan",
            "-s", "astar",
            "-H", "actionlandmark",
            task.domain.path,
            task.instance.path
        ]
    elif obj == "delete_relaxed_plan":
        extension = ".pddl.soln.rlx"
        command = [
            "pyperplan",
            "-s", "gbf",
            "-H", "hffpo",
            task.domain.path,
            task.instance.path
        ]
    elif obj == "plan":
        extension = ".pddl.soln"
        command = [
            "pyperplan",
            "-s", "gbf",
            "-H", "hff",
            task.domain.path,
            task.instance.path
        ]
    else:
        raise ValueError(f"Unknown object type: {obj}")
    if obj != "plan":
        path = task.get_solution_path(extension)
        if os.path.exists(path):
            with open(path, 'r') as f:
                content = f.read()
        else:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Error running pyperplan for task {task}: {result.stderr}")
            content = result.stdout
            with open(path, 'w') as f:
                f.write(content)
        return extract(content, obj)
    else:
        path = task.get_solution_path(extension)
        if not os.path.exists(path):
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"Error running pyperplan for task {task}: {result.stderr}")
        with open(path, 'r') as f:
            content = f.read()
        return content.splitlines()
            
def extract(content : str, obj: str, return_str: bool = False):
    if obj == "landmark":
        start_mark = "<action-landmarks-set>"
        end_mark = "</action-landmarks-set>"
    elif obj == "plan":
        start_mark = "<plan>"
        end_mark = "</plan>"
    elif obj == "delete_relaxed_plan":
        start_mark = "<delete-relaxed-plan>"
        end_mark = "</delete-relaxed-plan>"
    elif obj == "sample":
        start_mark = "<sample>"
        end_mark = "</sample>"
    elif obj == "domain":
        start_mark = "<domain-file>"
        end_mark = "</domain-file>"
    elif obj == "instance":
        start_mark = "<instance-file>"
        end_mark = "</instance-file>"
    elif obj == "metadata":
        start_mark = "<metadata>"
        end_mark = "</metadata>"
    elif obj == "response":
        start_mark = "<response>"
        end_mark = "</response>"
    else:
        raise ValueError(f"Unknown object type: {obj}")
    start_index = content.find(start_mark)
    end_index = content.find(end_mark)

    if start_index == -1 or end_index == -1:
        raise ValueError(f"Object {obj} not found in the output.")
    str_to_extract = content[start_index + len(start_mark):end_index].strip()

    extracted_items = []
    for line in str_to_extract.splitlines():
        stripped_line = line.strip()
        if stripped_line and stripped_line not in ["", "\n"]:
            extracted_items.append(stripped_line)

    if return_str:
        return "\n".join(extracted_items)
    else:
        return extracted_items

def val(domain_path : str, instance_path: str, plan_path : str, save_path: Optional[str]) -> tuple[bool, Optional[str]]:
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
    except subprocess.CalledProcessError as e:
        return False, f"Error validating plan: {e.stderr.strip()}"

    content = result.stdout
    if save_path:
        with open(save_path, 'w') as f:
            f.write(content)

    if "Error: Bad operator in plan!" in result.stderr:
        return False, "Error: Bad operator in plan."
    
    if "Error: Error in type-checking!" in result.stderr:
        return False, "Error: Error in type-checking."
    
    if "Plan failed to execute" in content:
        return False, "Error: Plan failed to execute."

    if "Bad plan description!" in content:
        return False, "Error: Bad plan description."

    if "Goal not satisfied" in content or "Plan invalid" in content:
        return False, "Error: Goal not satisfied."

    if "Plan executed successfully - checking goal" in content and "Plan valid" in content:
        return True, None

    return False, "Error: Unknown validation result."

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

from typing import Callable, Any, List
import os 
from reasoning.settings import EXPERIMENTS_DIR
def process_log_files(callback_fn: Callable[[str, str, str, str, str, str], Any], 
        continue_on_error: bool = True,
        verbose: bool = True) -> List[Any]:
        """
        Applies a callback function to each log file found in a nested directory structure.
        
        Args:
            callback_fn: Function that takes (exp, model, template, domain, instance_file) as arguments
            base_dir: The base directory to start the traversal
            continue_on_error: If True, continues processing after errors in the callback
            
        Returns:
            List of results from each callback invocation
        """
        results = []

        for exp in os.listdir(EXPERIMENTS_DIR):
            exp_dir = os.path.join(EXPERIMENTS_DIR, exp)
            if not os.path.isdir(exp_dir):
                continue

            for model in os.listdir(exp_dir):
                model_dir = os.path.join(exp_dir, model)
                if not os.path.isdir(model_dir):
                    continue

                for template in os.listdir(model_dir):
                    template_dir = os.path.join(model_dir, template)
                    if not os.path.isdir(template_dir):
                        continue

                    for domain in os.listdir(template_dir):
                        domain_dir = os.path.join(template_dir, domain)
                        if not os.path.isdir(domain_dir):
                            continue
                        
                        for instance in os.listdir(domain_dir):
                            instance_dir = os.path.join(domain_dir, instance)
                            if not os.path.isdir(instance_dir):
                                continue

                            for f in os.listdir(instance_dir):
                                if f.endswith(".log"):
                                    log_file = os.path.join(instance_dir, f)
                                    try:
                                        result = callback_fn(exp, model, template, domain, instance, log_file)
                                        results.append(result)
                                    except Exception as e:
                                        if verbose:
                                            print(f"Error processing {log_file}: {e}")
                                        if not continue_on_error:
                                            raise e
        return results
    
def sort_landmarks(task: Task, action_landmarks: list[str]) -> list[str]:
    soln_path = task.get_solution_path(".pddl.soln")
    if not os.path.exists(soln_path):
        raise RuntimeError(f"Solution file not found for task {task}: {soln_path}")

    with open(soln_path, 'r') as f:
        soln = f.read()

    def landmarks_value(landmark: str, soln: str) -> int:
        if landmark in soln:
            return soln.index(landmark)
        else:
            raise ValueError(f"Landmark {landmark} not found in solution.")
    # Sort the action landmarks based on their order in the solution
    sorted_landmarks = sorted(action_landmarks, key=lambda x: landmarks_value(x, soln))
    return sorted_landmarks