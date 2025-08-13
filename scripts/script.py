from reasoning.settings import SOLUTIONS_DIR
import os
from reasoning.utils import process_log_files, extract_landmarks

def take_landmarks_from_log_to_solution_file(
    exp: str, model: str, template: str, domain: str, instance_file: str
) -> None:
    if "landmark" not in template:
        return

    path = os.path.join(
        SOLUTIONS_DIR,
        domain,
        instance_file.split('/')[-1].replace('.log', '.pddl.lndmk')
    )

    if os.path.exists(path):
        return

    with open(instance_file, 'r') as f:
        content = f.read()
    landmarks = extract_landmarks(content)
    landmarks = ["<landmarks-set>"] + landmarks + ["</landmarks-set>"]
    with open(path, 'w') as f:
        for l in landmarks:
            f.write(f"{l}\n")

process_log_files(take_landmarks_from_log_to_solution_file, False)