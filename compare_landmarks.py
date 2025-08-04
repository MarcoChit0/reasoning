# for each domain on res/ipc2023-learning/benchmarks
#   for each instance
#     get the number of action landmarks
#     solve the instance with lmcut and the the plan length
# print the mean and std of the plan length
# print the mean and std of the number of action landmarks
# print the ratio of action landmarks to plan length

import os
import re
import subprocess

path = "res/ipc2023-learning/benchmarks"

import tqdm
data = []
for domain in os.listdir(path):
    domain_dir = os.path.join(path, domain)
    domain_path = os.path.join(domain_dir, "domain.pddl")
    if not os.path.isdir(domain_dir):
        continue
    if domain == "solutions":
        continue
    print(f"Processing domain: {domain}")
    instance_dir = os.path.join(domain_dir, "testing", "easy")
    instances = os.listdir(instance_dir)
    instances = [i for i in instances if i.endswith(".pddl")]
    progress = tqdm.tqdm(instances, desc=f"Processing instances in {domain}")
    for instance in progress:
        instance_path = os.path.join(instance_dir, instance)
        if not os.path.isfile(instance_path + ".landmarks"):
            continue
        with open(instance_path + ".landmarks", "r") as instance_file:
            output = instance_file.read()
            start_index = output.find("<landmarks-set>")
            end_index = output.find("</landmarks-set>")
            
            if start_index == -1 or end_index == -1:
                raise ValueError("Action landmarks not found in the output.")

            action_landmarks_str = output[start_index + len("<landmarks-set>"):end_index].strip()
            num_action_landmarks = 0
            for landmark in action_landmarks_str.splitlines():
                if landmark.strip() and landmark.strip() != "":
                    num_action_landmarks += 1

        plan_path = os.path.join(path, "solutions", domain, "testing", "easy", instance.replace(".pddl", ".plan"))
        _re = "; cost = (\d+) \(unit cost\)"
        with open(plan_path, "r") as plan_file:
            plan_output = plan_file.read()
            match = re.search(_re, plan_output)
            if not match:
                raise ValueError(f"Plan cost not found in the output for {instance_path}.")
            plan_length = int(match.group(1))

        data.append({
            "domain": domain,
            "instance": instance,
            "num_action_landmarks": num_action_landmarks,
            "plan_length": plan_length
        })

import pandas as pd

df = pd.DataFrame(data, columns=["domain", "instance", "num_action_landmarks", "plan_length"])
# Calculate the ratio for each row first
df["ratio"] = df["num_action_landmarks"] / df["plan_length"]
print(df)

gpf = df.groupby("domain").agg(
    mean_action_landmarks=("num_action_landmarks", "mean"),
    std_action_landmarks=("num_action_landmarks", "std"),
    mean_plan_length=("plan_length", "mean"),
    std_plan_length=("plan_length", "std"),
    mean_ratio=("ratio", "mean")
).reset_index()
print(gpf)
gpf.to_csv("action_landmarks.csv", index=False)