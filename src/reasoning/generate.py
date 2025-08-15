from datetime import time
import yaml
import tqdm
import os
import reasoning.models as models
from reasoning.task import Task, get_tasks
from reasoning.prompt import build_prompt
from reasoning.utils import from_config
import logging
from reasoning.settings import EXPERIMENTS_DIR, SAMPLE_FILE_NAME, PROMPT_FILE_NAME
import pandas as pd
from datetime import datetime

def save_model_metadata(df: pd.DataFrame, path: str):
    import os
    try:
        # Check if file exists
        if os.path.exists(path):
            # Load existing data
            existing_df = pd.read_csv(path)
            
            # Create a composite key for matching rows
            key_columns = ["template", "domain", "instance", "sample_id"]
            
            # Merge DataFrames based on key columns
            # This will update existing rows and add new ones
            merged_df = pd.concat([existing_df, df])
            merged_df = merged_df.drop_duplicates(subset=key_columns, keep='last')
            
            # Save the merged DataFrame
            merged_df.to_csv(path, index=False)
        else:
            # File doesn't exist, create it
            df.to_csv(path, index=False)
    except Exception as e:
        print(f"Error saving metadata: {e}")
        # Fallback to simple save
        df.to_csv(path, index=False)



def generate(model: models.Model, tasks: list[Task], template: str, samples: int, experiment: str, model_dir: str, **kwargs):
    """
    Generates responses for a list of tasks and saves them to a structured directory.

    New structure: <experiment>/<model>/<template>/<domain>/<instance>/
    - prompt.log: Contains the prompt and its metadata.
    - sample_<num>.log: Contains a single model response and its metadata.
    """
    metadata_list = []
    for task in tqdm.tqdm(tasks, desc="Generating content", unit="task"):
        # Define the new base directory for the instance
        instance_dir = os.path.join(
            EXPERIMENTS_DIR,
            experiment,
            model_dir,
            template,
            task.domain.name,
            task.instance.name, # New structure uses instance name as the directory
        )
        os.makedirs(instance_dir, exist_ok=True)
        prompt_log_file = os.path.join(instance_dir, PROMPT_FILE_NAME)
        try:
            # Build the prompt
            prompt = build_prompt(task, template)
            prompt_metadata = prompt["metadata"]
            prompt_text = prompt["prompt"]

            # Save the prompt and its metadata to prompt.log
            if not os.path.exists(prompt_log_file):
                with open(prompt_log_file, 'w') as prompt_file:
                    prompt_file.write(f"[{datetime.now()}] Task: {task}\n")
                    prompt_file.write(f"[{datetime.now()}] Model: {model.name}\n")
                    prompt_file.write(f"[{datetime.now()}] Generation Parameters: {kwargs}\n")
                    prompt_file.write(f"[{datetime.now()}]\nPrompt Metadata:\n")
                    prompt_file.write(f"<metadata>\n{prompt_metadata}\n</metadata>\n\n")
                    prompt_file.write(f"[{datetime.now()}]\nPrompt:\n")
                    prompt_file.write(f"<prompt>\n{prompt_text}\n</prompt>\n")

            # Generate and save each sample
            for i in range(1, samples + 1):
                sample_log_file = os.path.join(instance_dir, SAMPLE_FILE_NAME.format(i))
                if os.path.exists(sample_log_file):
                    continue

                sample_file = open(sample_log_file, 'w')
                if not sample_file:
                    continue

                try:
                    sample_file.write(f"[{datetime.now()}] Generating response for sample {i}.\n")
                    response = model.generate_response(prompt=prompt_text, **kwargs)
                    sample_file.write(f"[{datetime.now()}] Response for sample {i} generated successfully.\n")

                    sample_file.write(f"[{datetime.now()}] Response:\n")
                    sample_file.write(f"<response>\n{response['response']}\n</response>\n")

                    metadata = {
                        "template": template,
                        "domain": task.domain.name,
                        "instance": task.instance.name,
                        "sample_id": i,
                        **response['metadata']
                    }
                    metadata_list.append(metadata)

                    sample_file.write(f"[{datetime.now()}] Metadata:\n")
                    sample_file.write(f"<metadata>\n{str(metadata)}\n</metadata>\n")

                except RuntimeError as e:
                    sample_file.write(f"[{datetime.now()}] Error during sample generation: {e}\n")

                finally:
                    sample_file.close()

        except ValueError as e:
            with open(prompt_log_file + ".err", 'w') as error_f:
                error_f.write(f"[{datetime.now()}] Error building prompt for task {task}: {e}\n")

    # Save all collected metadata to a single CSV file for the model
    if metadata_list:
        metadata_df = pd.DataFrame(metadata_list)
        save_model_metadata(
            metadata_df, 
            os.path.join(EXPERIMENTS_DIR, experiment, model_dir, "metadata.csv")
        )

if __name__ == "__main__":
    experiment = "3-samples"
    samples = 3
    templates = ["ordered_landmark_explicit", "ordered_landmark_omitted"]
    domains = ["logistics", "blocksworld"]
    config_paths = [
        "src/configs/gemini-thinking.yaml",
    ]

    for config_path in config_paths:
        config = from_config(config_path)
        model_config = config.get("model_config", {})
        generation_config = config.get("generation_config", {})
        model_dir = config_path.split('/')[-1].replace('.yaml', '').strip()
        try:
            model = models.get_model_from_model_config(**model_config)
        except Exception as e:
            raise ValueError(f"Error initializing model with model_config: {model_config}. Error: {e}")
        for template in templates:
            for domain in domains:
                try:
                    tasks = sorted(get_tasks(domain))
                    tasks = tasks[-20:]
                except ValueError as e:
                    raise ValueError(f"Error getting tasks for domain '{domain}': {e}")
                print(f"Experiment: {experiment}\nModel: {model.name}\nDomain: {domain}\nTemplate: {template}\nSamples: {samples}\nGeneration Config: {generation_config}\n")
                generate(
                    model=model,
                    tasks=tasks,
                    template=template,
                    samples=samples,
                    experiment=experiment,
                    model_dir=model_dir,
                    **generation_config
                )
