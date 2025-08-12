import os
import pandas as pd

def extract_landmarks(content : str) -> list[str]:
    """
    content:
    '...
    <landmarks-set>
    l1
    l2
    ...
    ln
    </landmarks-set>
    ...'
    l1, l2, ..., ln are the landmarks
    """
    content = content.splitlines()
    landmarks = []
    in_landmarks = False
    for line in content:
        if "<landmarks-set>" in line:
            in_landmarks = True
            continue
        if "</landmarks-set>" in line:
            in_landmarks = False
            continue
        if in_landmarks:
            landmarks.append(line.strip())
    return landmarks


def extract_plan(content: str) -> list[str]:
    """
    content:
    '...
    <plan>
    a1
    a2
    ...
    an
    </plan>
    ...'
    a1, a2, ..., an are the actions in the plan
    """
    content = content.splitlines()
    plans = []
    in_plans = False
    for line in content:
        if "<plan>" in line:
            in_plans = True
            continue
        if "</plan>" in line:
            in_plans = False
            continue
        if in_plans:
            plans.append(line.strip())
    return plans

base_dir = "./data/experiments"
from reasoning.utils import process_log_files

def check_landmarks_usage(experiment, model, template, domain, instance_file):
    with open(instance_file, 'r') as f:
        instance_content = f.read()
    actions = extract_plan(instance_content)
    landmarks = extract_landmarks(instance_content)
    num_landmarks = len(landmarks)
    if num_landmarks == 0:
        # try checking whether log files from template = "landmark" or "new_landmark"
        found = False
        for ltemp in ["landmark", "new_landmark"]:
            new_path = instance_file.replace(template, ltemp)
            if new_path != instance_file:
                with open(new_path, 'r') as f:
                    instance_content = f.read()
                landmarks = extract_landmarks(instance_content)
                num_landmarks = len(landmarks)
                if num_landmarks > 0:
                    found = True
                    break
        if not found:
            raise ValueError(f"No landmarks found in log file {instance_file} or alternatives.")
    if len(actions) == 0:
        used_ratio = 0
        used_landmarks = 0
    else:
        sl = set(landmarks)
        sa = set(actions)
        used_landmarks = len(sl.intersection(sa))
        used_ratio = used_landmarks / num_landmarks
    return {
        "experiment" : experiment,
        "domain": domain,
        "model": model,
        "template": template,
        "instance": instance_file,
        "num_landmarks": num_landmarks,
        "used_landmarks": used_landmarks,
        "used_ratio": used_ratio
    }

data = process_log_files(check_landmarks_usage, False)
df = pd.DataFrame(data)

from reasoning.settings import EXPERIMENTS_DIR
for exp_dir in os.listdir(EXPERIMENTS_DIR):
    if not os.path.isdir(os.path.join(EXPERIMENTS_DIR, exp_dir)): continue
    exp_df = df[df['experiment'] == exp_dir]
    exp_df.to_csv(os.path.join(EXPERIMENTS_DIR, exp_dir, "landmark_usage.csv"), index=False, float_format='%.2f')

    grouped_exp_df = exp_df.groupby(['domain', 'model', 'template']).agg({
        'num_landmarks': 'mean',
        'used_landmarks': 'mean',
        'used_ratio': 'mean',
        'instance' : 'count'
    }).reset_index()

    grouped_exp_df.to_csv(os.path.join(EXPERIMENTS_DIR, exp_dir, "landmark_usage_grouped.csv"), index=False, float_format='%.2f')
