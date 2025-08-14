import os
from reasoning.utils import val, process_log_files
import pandas as pd
import ast
from reasoning.settings import PROMPT_FILE_NAME, VALIDATED_LOG_FILE_FILE_NAME, VALIDATION_FILE_NAME, EXPERIMENTS_DIR, ERROR_TYPES_FILE_NAME

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

from reasoning.utils import extract
import re
def validate_log_file(experiment : str, model : str, template : str, domain : str, instance : str, log_file : str) -> None:
    if not os.path.exists(log_file):
        raise FileNotFoundError(f"Log file {log_file} does not exist.")

    pattern = r"sample_(\d+).log"
    if not re.search(pattern, log_file):
        raise ValueError(f"Invalid log file format: {log_file}")

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
        domain_content = extract(prompt_content, "domain")
    except ValueError as e:
        raise ValueError(f"Domain extraction failed on file {prompt_file}: {e}")

    try:
        instance_content = extract(prompt_content, "instance")
    except ValueError as e:
        raise ValueError(f"Instance extraction failed on file {prompt_file}: {e}")

    
    with open(log_file, 'r') as f:
        log_content = f.read()

    valid, error = False, None
    try:
        response = extract(log_content, "response")
        try:
            plan = extract(log_content, "plan")
            with open(temp_domain_file, 'w') as f:
                for l in domain_content:
                    f.write(f"{l}\n")
            with open(temp_instance_file, 'w') as f:
                for l in instance_content:
                    f.write(f"{l}\n")
            with open(temp_plan_file, 'w') as f:
                for action in plan:
                    f.write(f"{action}\n")
            
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
    
    return {
        "experiment": experiment,
        "model": model,
        "template": template,
        "domain": domain,
        "instance": instance,
        "sample_id": sample_id,
        "valid": valid,
        "error": error
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


data = process_log_files(validate_log_file, continue_on_error=True)

df = pd.DataFrame(data)
if not len(data) == 0:
    for experiment in os.listdir(EXPERIMENTS_DIR):
        experiment_dir = os.path.join(EXPERIMENTS_DIR, experiment)
        if os.path.isdir(experiment_dir):
            exp_df = df[df["experiment"] == experiment]
            if exp_df.empty:
                continue
            exp_df.reset_index(drop=True, inplace=True)
            exp_df.to_csv(os.path.join(experiment_dir, VALIDATION_FILE_NAME))
            analyze_error_type(exp_df, experiment_dir)


