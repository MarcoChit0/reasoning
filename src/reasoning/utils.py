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
<action_landmarks>
(pick-up b)
(stack b a)
(unstack c b)
</action_landmarks>
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
    start_index = output.find("<action_landmarks>")
    end_index = output.find("</action_landmarks>")
    
    if start_index == -1 or end_index == -1:
        raise ValueError("Action landmarks not found in the output.")

    action_landmarks_str = output[start_index + len("<action_landmarks>"):end_index].strip()
    action_landmarks = action_landmarks_str.splitlines()
    
    return [landmark.strip() for landmark in action_landmarks if landmark.strip()]

if __name__ == "__main__":
    from reasoning.task import get_tasks_from_raw

    domain = "storage"
    
    tasks = get_tasks_from_raw(domain)
    m = {}
    for task in tasks:
        try:
            landmarks = get_action_landmarks(task)
            if len(landmarks) > 0:
                if len(landmarks) not in m:
                    m[len(landmarks)] = []
                m[len(landmarks)].append(task.instance.name)
        except Exception as e:
            print(f"Error getting action landmarks for task {task.instance.name}: {e}")
    
    max_len = max(m.keys())
    print(f"Max action landmarks: {max_len}")
    print(f"Tasks with {max_len} action landmarks:")
    print(m[max_len])
