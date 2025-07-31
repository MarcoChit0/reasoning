import os
from reasoning.utils import call_val
import pandas as pd

def process_sample(sample: str) -> str:
    error_fidx = sample.find("<error>")
    error_lidx = sample.find("</error>")
    if error_fidx != -1 and error_lidx != -1:
        raise ValueError(f"Sample contains an error: {sample[error_fidx + len('<error>'):error_lidx].strip()}")

    response_fidx = sample.find("<response>")
    response_lidx = sample.find("</response>")
    if response_fidx == -1 or response_lidx == -1:
        raise ValueError("Response not found in sample.")
    if response_fidx > response_lidx:
        raise ValueError("Malformed sample: <response> tag appears after </response>.")
    response = sample[response_fidx + len("<response>"):response_lidx].strip()
    if not response:
        raise ValueError("Empty response in sample.")

    plan_fidx = response.find("<plan>")
    plan_lidx = response.find("</plan>")
    if plan_fidx == -1 or plan_lidx == -1:
        raise ValueError("Plan not found in response.")
    if plan_fidx > plan_lidx:
        raise ValueError("Malformed response: <plan> tag appears after </plan>.")
    plan = response[plan_fidx + len("<plan>"):plan_lidx].strip()
    if not plan:
        raise ValueError("Empty plan in response.")
    return plan

def validate_experiment(experiment_path: str) -> None:
    """
    Validate an experiment.
    The experiment structure should be the following:
    experiment_path/
        <config_name>/
            <template>/
                <domain>/
                    <instance_type>/
                        <instance_file>.log
                        ...
                    ...
                ...
            ...
        ...
    
    It returns a CSV file with the validation results in the experiment_path.
    Each row contains:
    - config_name
    - template
    - domain
    - instance_type
    - instance
    - sample_id
    - valid (True/False)
    - error (if any)
    """
    from reasoning.settings import VALIDATION_FILE_NAME
    data = []
    experiment = experiment_path.split('/')[-1].strip()
    print(f"Experiment: {experiment}")
    for config_name in os.listdir(experiment_path):
        config_path = os.path.join(experiment_path, config_name)
        if not os.path.isdir(config_path):
            continue
        print(f"\tConfig: {config_name}")
        
        for template in os.listdir(config_path):
            template_path = os.path.join(config_path, template)
            if not os.path.isdir(template_path):
                continue    
            print(f"\t\tTemplate: {template}")

            for domain in os.listdir(template_path):
                domain_path = os.path.join(template_path, domain)
                if not os.path.isdir(domain_path):
                    continue
                print(f"\t\t\tDomain: {domain}")
                temp_domain_path = os.path.join(domain_path, "temp_domain.pddl")

                for instance_type in os.listdir(domain_path):
                    instance_type_path = os.path.join(domain_path, instance_type)
                    if not os.path.isdir(instance_type_path):
                        continue
                    print(f"\t\t\t\tInstance Type: {instance_type}")

                    for instance_file in os.listdir(instance_type_path):
                        if not instance_file.endswith(".log"):
                            continue
                        instance = instance_file.replace(".log", "")
                        instance_path = os.path.join(instance_type_path, instance_file)
                        temp_instance_path = os.path.join(instance_type_path, "temp_instance.pddl")
                        

                        with open(instance_path, 'r') as f:
                            content = f.read()

                        try:
                            _domain = content[content.find("<domain-file>") + len("<domain-file>"):content.find("</domain-file>")]
                            _instance = content[content.find("<instance-file>") + len("<instance-file>"):content.find("</instance-file>")]
                        
                            if not os.path.exists(temp_domain_path):
                                with open(temp_domain_path, 'w') as f:
                                    f.write(_domain)
                            with open(temp_instance_path, 'w') as f:
                                f.write(_instance)
                        except:
                            raise ValueError(f"Could not properly parse domain {domain} and instance from {instance_file}.")


                        samples = []
                        while True:
                            start_index = content.find("<sample>")
                            end_index = content.find("</sample>")
                            if start_index == -1 or end_index == -1:
                                break

                            sample = content[start_index + len("<sample>"):end_index].strip()
                            samples.append(sample)
                            content = content[end_index + len("</sample>"):].strip()

                        sample_id = 0
                        for sample in samples:
                            sample_id += 1
                            error = None
                            valid = False
                            try:
                                plan = process_sample(sample)
                                temp_plan_path = os.path.join(instance_type_path, "temp_plan.txt")
                                with open(temp_plan_path, 'w') as f:
                                    f.write(plan)
                                try:
                                    response = call_val(temp_domain_path, temp_instance_path, temp_plan_path)
                                    for line in response.splitlines():
                                        if "Plan valid" in line:
                                            valid = True
                                            break
                                except Exception as e:
                                    error = "Error when calling VAL: " + str(e)
                                finally:
                                    if os.path.exists(temp_plan_path): os.remove(temp_plan_path)

                            except Exception as e:
                                error = "Error processing Sample {}: {}".format(sample_id, str(e))
                            finally:
                                data.append({
                                    "experiment": experiment,
                                    "config_name": config_name,
                                    "template": template,
                                    "domain": domain,
                                    "instance_type": instance_type,
                                    "instance": instance,
                                    "sample_id": sample_id,
                                    "valid": valid,
                                    "error": error
                                })

                        if os.path.exists(temp_instance_path): os.remove(temp_instance_path)
                if os.path.exists(temp_domain_path): os.remove(temp_domain_path)
    if len(data) == 0:
        return
    df = pd.DataFrame(data)
    df.reset_index(drop=True, inplace=True)  # drop=True to avoid creating an extra column
    print(data)
    df.columns = data[-1].keys()
    df.to_csv(os.path.join(experiment_path, VALIDATION_FILE_NAME))

if __name__ == "__main__":
    from reasoning.settings import EXPERIMENTS_DIR
    
    if os.path.isdir(EXPERIMENTS_DIR):
        for experiment in os.listdir(EXPERIMENTS_DIR):
            experiment_path = os.path.join(EXPERIMENTS_DIR, experiment)
            if os.path.isdir(experiment_path):
                validate_experiment(experiment_path)