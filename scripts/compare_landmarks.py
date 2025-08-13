from reasoning.settings import SOLUTIONS_DIR

import os

data = {}
for domain in os.listdir(SOLUTIONS_DIR):
    domain_path = os.path.join(SOLUTIONS_DIR, domain)
    if not os.path.isdir(domain_path):
        continue

    dom_data = {}
    for file in os.listdir(domain_path):
        instance = file.split(".")[0]
        if instance not in dom_data:
            dom_data[instance] = {}
        if file.endswith(".soln"):
            with open(os.path.join(domain_path, file), 'r') as f:
                c = 0
                for line in f.readlines():
                    if line.strip() not in ["", "\n"]:
                        c += 1
                dom_data[instance]["plan"] = c
        if file.endswith(".lndmk"):
            with open(os.path.join(domain_path, file), 'r') as f:
                start = False
                c = 0
                for line in f.readlines():
                    if line.strip() == "<landmarks-set>":
                        start = True
                    elif line.strip() == "</landmarks-set>":
                        start = False
                    elif start and line.strip() != "":
                        c += 1
                dom_data[instance]["landmarks"] = c
    data[domain] = dom_data

# take the avg of the plans and landmarks
# take the ratio of the landmarks to the plans

import pandas as pd
import numpy as np

df = pd.DataFrame(columns=["domain", "plans", "landmarks", "ratio", "num_instances"])
for domain, instances in data.items():
    plans = []
    landmarks = []
    for instance, values in instances.items():
        p = values.get("plan", None)
        l = values.get("landmarks", None)
        if p is None or l is None:
            continue
        plans.append(p)
        landmarks.append(l)
    df = df._append({
        "domain": domain,
        "plans": np.mean(plans) if plans else 0,
        "landmarks": np.mean(landmarks) if landmarks else 0,
        "ratio": np.mean(landmarks) / np.mean(plans) if plans else 0,
        "num_instances": len(plans)
    }, ignore_index=True)

print(df)

