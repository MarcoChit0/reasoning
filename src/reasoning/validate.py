import os
from reasoning.utils import val
import pandas as pd
import ast

def process_sample(sample: str) -> tuple[str, dict[str, str]]:
    # This function remains the same
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
    
    metadata_fidx = sample.find("<metadata>")
    metadata_lidx = sample.find("</metadata>")
    if metadata_fidx != -1 and metadata_lidx != -1:
        metadata = sample[metadata_fidx + len("<metadata>"):metadata_lidx].strip()
        metadata = ast.literal_eval(metadata)
    else:
        metadata = {}

    return plan, metadata

def validate_experiment(experiment_path: str) -> None:
    """
    Validate an experiment.
    The experiment structure should be the following:
    experiment_path/
        <model>/
            <template>/
                <domain>/
                    <instance_subdir>*/
                        <instance>.log
                    ...
                ...
            ...
        ...
    
    It returns a CSV file with the validation results in the experiment_path.
    Each row contains:
    - experiment
    - domain
    - instance_subdir (path after domain directory)
    - model
    - template
    - instance
    - sample_id
    - valid (True/False)
    - error (if any)
    """
    from reasoning.settings import VALIDATION_FILE_NAME
    data = []
    experiment = experiment_path.split('/')[-1].strip()
    print(f"Experiment: {experiment}")
    
    for model in os.listdir(experiment_path):
        model_path = os.path.join(experiment_path, model)
        if not os.path.isdir(model_path):
            continue
        print(f"\tModel: {model}")
        
        for template in os.listdir(model_path):
            template_path = os.path.join(model_path, template)
            if not os.path.isdir(template_path):
                continue    
            print(f"\t\tTemplate: {template}")
            
            for domain in os.listdir(template_path):
                domain_path = os.path.join(template_path, domain)
                if not os.path.isdir(domain_path):
                    continue
                print(f"\t\t\tDomain: {domain}")
                temp_domain_path = os.path.join(domain_path, "temp_domain.pddl")
                
                # Process all log files under this domain directory
                for root, _, files in os.walk(domain_path):
                    for instance_file in files:
                        if not instance_file.endswith(".log"):
                            continue
                            
                        instance = instance_file.replace(".log", "")
                        instance_path = os.path.join(root, instance_file)
                        
                        # Get the relative path from domain directory to instance directory
                        relative_path = os.path.relpath(root, domain_path)
                        instance_subdir = relative_path if relative_path != "." else ""
                        
                        print(f"\t\t\t\tInstance: {instance_subdir}/{instance}")
                        
                        temp_instance_path = os.path.join(root, "temp_instance.pddl")
                        
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
                        
                        prompt_metadata = {}
                        try:
                            prompt_metadata_fidx = content.find("<prompt_metadata>")
                            prompt_metadata_lidx = content.find("</prompt_metadata>")
                            if prompt_metadata_fidx != -1 and prompt_metadata_lidx != -1:
                                metadata_str = content[prompt_metadata_fidx + len("<prompt_metadata>"):prompt_metadata_lidx].strip()
                                if metadata_str:
                                    prompt_metadata = ast.literal_eval(metadata_str)
                        except Exception:
                            # If metadata is malformed, we treat it as empty.
                            prompt_metadata = {}

                        samples = []
                        temp_content = content
                        while True:
                            start_index = temp_content.find("<sample>")
                            end_index = temp_content.find("</sample>")
                            if start_index == -1 or end_index == -1:
                                break

                            sample = temp_content[start_index + len("<sample>"):end_index].strip()
                            samples.append(sample)
                            temp_content = temp_content[end_index + len("</sample>"):].strip()

                        sample_id = 0
                        for sample in samples:
                            sample_id += 1
                            error = None
                            valid = False
                            plan_metadata = {}
                            try:
                                plan, plan_metadata = process_sample(sample)
                                temp_plan_path = os.path.join(root, "temp_plan.txt")
                                with open(temp_plan_path, 'w') as f:
                                    f.write(plan)
                                try:
                                    valid, error = val(temp_domain_path, temp_instance_path, temp_plan_path)
                                    if os.path.exists(temp_plan_path): os.remove(temp_plan_path)
                                except Exception as e:
                                    raise RuntimeError(f"Error validating plan: {str(e)}")

                            except Exception as e:
                                error = "Error processing Sample {}: {}".format(sample_id, str(e))
                            finally:
                                num_action_landmarks = prompt_metadata.get("num_action_landmarks", None)
                                candidates_token_count = plan_metadata.get("candidates_token_count", None)

                                data.append({
                                    "experiment": experiment,
                                    "domain": domain,
                                    "instance_subdir": instance_subdir,
                                    "model": model,
                                    "template": template,
                                    "instance": instance,
                                    "sample_id": sample_id,
                                    "valid": valid,
                                    "error": error,
                                    "num_action_landmarks": num_action_landmarks,
                                    "candidates_token_count": candidates_token_count
                                })

                        if os.path.exists(temp_instance_path): os.remove(temp_instance_path)
                if os.path.exists(temp_domain_path): os.remove(temp_domain_path)
    
    if len(data) == 0:
        return
    df = pd.DataFrame(data)
    df.reset_index(drop=True, inplace=True)  # drop=True to avoid creating an extra column
    df.to_csv(os.path.join(experiment_path, VALIDATION_FILE_NAME))

    """
    Group the data [experiment, model, template, domain] and analyze error types.
    possibilities:
        Error processing Sample <num>: <error>
        Error: Goal not satisfied.
        Error: Plan failed to execute.
        Error: Unknown validation result.
        Error: Bad operator in plan.
        Error: Error in type-checking.
        Error: Bad plan description.
        Error: Unknown validation result.
        None
    Each line of the new table should be the count of instances for (experiment, model, template, domain). 
    Each column should be the error type.
    The first type of error can have different kind of suberrors on <error>, each one should have a new column. The first type of error can be repeated for each sample <num>. A new column should not be created if the only thing changing is the sample number. Its column name can be compressed as Error: <error>
    """
    
    import re
    # Process error messages to extract actual error types
    def extract_error_type(error):
        if pd.isna(error):
            return "Valid Plan"
        
        # For "Error processing Sample <num>: <error>" extract the actual error
        sample_error_match = re.match(r"Error processing Sample \d+: (.*)", error)
        if sample_error_match:
            return f"Error: Sample with processing issue."

        return error
    
    # Apply error type extraction
    df['error_type'] = df['error'].apply(extract_error_type)
    
    # Use crosstab which is more appropriate for counting occurrences
    error_analysis = pd.crosstab(
        index=[df['experiment'], df['model'], df['template'], df['domain']],
        columns=df['error_type'],
        margins=True,
        margins_name='Total'
    )
    
    # Truncate long column names to 30 characters
    error_analysis.columns = [str(col)[:27] + '...' if len(str(col)) > 30 else col for col in error_analysis.columns]
    
    # save to csv
    from reasoning.settings import ERROR_TYPES_FILE_NAME
    output_file = os.path.join(experiment_path, ERROR_TYPES_FILE_NAME)
    error_analysis.to_csv(output_file)
    print(f"Validation error analysis saved to {output_file}")
    

if __name__ == "__main__":
    from reasoning.settings import EXPERIMENTS_DIR
    
    if os.path.isdir(EXPERIMENTS_DIR):
        for experiment in os.listdir(EXPERIMENTS_DIR):
            experiment_path = os.path.join(EXPERIMENTS_DIR, experiment)
            if os.path.isdir(experiment_path):
                validate_experiment(experiment_path)