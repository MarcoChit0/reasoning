import os
from reasoning.utils import val, process_log_files
import pandas as pd
from reasoning.settings import PROMPT_FILE_NAME, VALIDATED_LOG_FILE_FILE_NAME, VALIDATION_FILE_NAME, EXPERIMENTS_DIR, ERROR_TYPES_FILE_NAME, BENCHMARKS_DIR, SOLUTIONS_DIR_NAME

from reasoning.utils import extract
import re

def validate_log_file(experiment : str, model : str, template : str, domain : str, instance : str, log_file : str ) -> None:
    pattern = r"sample_(\d+).log"
    log_file_name = log_file.split("/")[-1].strip()
    if not re.match(pattern, log_file_name):
        raise ValueError(f"Log file {log_file} does not match expected pattern.")
    sample_id = re.search(pattern, log_file).group(1)
    log_dir = os.path.dirname(log_file)
    prompt_file = os.path.join(log_dir, PROMPT_FILE_NAME)
    val_file = os.path.join(log_dir, VALIDATED_LOG_FILE_FILE_NAME.format(sample_id))
    temp_domain_file = "temp_domain.pddl"
    temp_instance_file = "temp_instance.pddl"
    temp_plan_file = "temp_plan.pddl"

    if not os.path.exists(prompt_file):
        raise FileNotFoundError(f"Prompt file {prompt_file} does not exist.")
    
    with open(prompt_file, 'r') as f:
        prompt_content = f.read()

    try:
        domain_content = extract(prompt_content, "domain", return_str=True)
    except ValueError as e:
        raise ValueError(f"Domain extraction failed on file {prompt_file}: {e}")

    try:
        instance_content = extract(prompt_content, "instance", return_str=True)
    except ValueError as e:
        raise ValueError(f"Instance extraction failed on file {prompt_file}: {e}")

    with open(log_file, 'r') as f:
        log_content = f.read()

    plan = []
    valid, error = False, None
    try:
        response = extract(log_content, "response", return_str=True)
        try:
            plan = extract(response, "plan")
            with open(temp_domain_file, 'w') as f:
                f.write(domain_content)
            with open(temp_instance_file, 'w') as f:
                f.write(instance_content)
            with open(temp_plan_file, 'w') as f:
                f.write("\n".join(plan))

            try:
                valid, error = val(temp_domain_file, temp_instance_file, temp_plan_file, val_file)

            except RuntimeError as e:
                raise RuntimeError(f"Validation failed: {e}")
        except ValueError as e:
            error = f"Plan extraction failed : {e}"
    except ValueError as e:
        error = f"Response extraction failed : {e}"
    finally:
        if os.path.exists(temp_domain_file):
            os.remove(temp_domain_file)
        if os.path.exists(temp_instance_file):
            os.remove(temp_instance_file)
        if os.path.exists(temp_plan_file):
            os.remove(temp_plan_file)

    metadata = {}
    landmarks_file = os.path.join(BENCHMARKS_DIR, domain, SOLUTIONS_DIR_NAME, instance + ".pddl.lndmk")
    if not os.path.exists(landmarks_file):
        raise FileNotFoundError(f"Landmarks file {landmarks_file} does not exist.")

    with open(landmarks_file) as f:
        content = f.read()
    action_landmarks = set(extract(content, "landmark"))
    used_action_landmarks = action_landmarks.intersection(set(plan))
    metadata.update({
        "num_action_landmarks": len(action_landmarks),
        "num_action_landmarks_used": len(used_action_landmarks)
    })

    return {
        "experiment": experiment,
        "model": model,
        "template": template,
        "domain": domain,
        "instance": instance,
        "sample_id": sample_id,
        "valid": valid,
        "error": error,
        **metadata
    }


def analyze_error_type(df: pd.DataFrame, experiment_path):
    # Process error messages to extract actual error types
    def extract_error_type(error:str) -> str:
        if pd.isna(error):
            return "Valid Plan"
        
        else:
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
    output_file = os.path.join(experiment_path, ERROR_TYPES_FILE_NAME)
    error_analysis.to_csv(output_file)
    print(f"Validation error analysis saved to {output_file}")


data = process_log_files(callback_fn=validate_log_file, continue_on_error=True, verbose=False)

response_df = pd.DataFrame(data)

if not response_df.empty:
    for experiment in os.listdir(EXPERIMENTS_DIR):
        experiment_dir = os.path.join(EXPERIMENTS_DIR, experiment)
        if not os.path.isdir(experiment_dir): continue 

        exp_df = response_df[response_df["experiment"] == experiment].copy()
        if not exp_df.empty:
            exp_df.reset_index(drop=True, inplace=True)
            exp_df.to_csv(os.path.join(experiment_dir, VALIDATION_FILE_NAME))
            print(f"Validation results saved to {os.path.join(experiment_dir, VALIDATION_FILE_NAME)}")
            analyze_error_type(exp_df, experiment_dir)