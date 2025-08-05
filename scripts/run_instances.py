import os
import subprocess
import resource

for domain in os.listdir("data/benchmarks"):
    domain_path = os.path.join("data/benchmarks", domain)
    if os.path.isdir(domain_path):
        instances_path = os.path.join(domain_path, "instances")
        if not os.path.exists(instances_path):
            continue

        # there are subdirectories between ./data/benchmarks/<domain>/instances and the actual instances
        # precisely ./data/benchmarks/<domain>/instances/<subdir>/.../<subdir>/<instance>.pddl
        for root, dirs, files in os.walk(instances_path):
            for file in files:
                if file.endswith(".pddl"):
                    instance_file = os.path.join(root, file)
                    print(f"Processing {instance_file} in domain {domain}")
                    command = [
                        "python",
                        "res/pyperplan/pyperplan",
                        os.path.join(domain_path, "domain.pddl"),
                        instance_file,
                        "-s", "astar",
                        "-H", "hff",
                    ]
                    try:
                        result = subprocess.run(command, capture_output=True, text=True, timeout=1800, 
                                               preexec_fn=lambda: resource.setrlimit(resource.RLIMIT_AS, (24 * 1024**3, 24 * 1024**3)))
                        output_file = instance_file + ".soln"
                        
                        # Read the solution file and count lines
                        if os.path.exists(output_file):
                            with open(output_file, "r") as f:
                                line_count = len(f.readlines())
                            
                            # Write to CSV file
                            csv_file = "results.csv"
                            with open(csv_file, "a") as f:
                                f.write(f"{domain},{os.path.basename(instance_file)},{line_count}\n")
                            input()
                    except subprocess.CalledProcessError as e:
                        print(f"Error executing pyperplan command: {e}")
                        print(f"Error output: {e.stderr}")
                    except subprocess.TimeoutExpired as e:
                        print(f"Timeout expired for instance {instance_file}: {e}")