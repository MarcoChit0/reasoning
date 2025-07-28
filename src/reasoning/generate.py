from datetime import time
import dotenv
import yaml
import tqdm
import os
from reasoning.model import GoogleModel
from reasoning.task import Task, get_tasks_from_raw
from reasoning.prompt import build_prompt
import logging
import numpy as np
import time

dotenv.load_dotenv()
api_key = dotenv.get_key(dotenv.find_dotenv(), "GOOGLE_API_KEY")

with open("src/configs/gemini.yaml", 'r') as f:
    config = yaml.safe_load(f)

model_name = config.get("model_name", None)
assert model_name is not None, "Model name must be specified in the configuration file."
model = GoogleModel(
    model_name=model_name,
    api_key=api_key
)
wait_time = config.get("wait_time", 0)
generation_config = config.get("generation_config", {})

template = "landmark"
instances = 1
samples = 1
domain = "hanoi"
experiment = "test-landmark"
instance_type = "outdistribution"

path = os.path.join("data", "experiments", experiment, domain, instance_type)
os.makedirs(path, exist_ok=True)

tasks : list[Task] = get_tasks_from_raw(domain, instance_type=instance_type)
print(f"Found {len(tasks)} tasks for domain '{domain}' with instance type '{instance_type}'.")

# Equally distribute tasks
if instances < len(tasks):
    idx = np.linspace(0, len(tasks) - 1, num=instances, dtype=int)
    tasks = [tasks[i] for i in idx]

already_generated_instances = [f.split(".")[0] for f in os.listdir(path) if f.endswith(".log")]
print(f"Already generated instances: {len(already_generated_instances)}")

tasks = [task for task in tasks if task.instance not in already_generated_instances]
print(f"Remaining tasks to generate: {len(tasks)}")

progress_bar = tqdm.tqdm(total=len(tasks) * samples, desc="Generating content", unit="sample")

for task in tasks:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    log_file = os.path.join(path, f"{task.instance.name}.log")
    handler = logging.FileHandler(log_file, mode='w')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    try:
        logging.info(f"Processing task: {task}")
        logging.info(f"Using model: {model_name}")
        logging.info(f"Generation parameters: {generation_config}")
        prompt = build_prompt(task, template, logger)
        for i in range(samples):
            logging.info(f"Sample: {i + 1}.")
            sample = "\n<sample>\n"
            try:
                response = model.generate_response(prompt, **generation_config)
                sample += f"<response>\n{response['response']}\n</response>\n"
                sample += f"<metadata>\n{str(response['metadata'])}\n</metadata>\n"
                success = True
            except RuntimeError as e:
                sample += f"<error>\n{str(e)}\n</error>\n"
                success = False
            finally:
                sample += "</sample>\n"
                if success:
                    logging.info(sample)
                else:
                    logging.error(sample)
                progress_bar.update(1)
                
            if wait_time > 0:
                time.sleep(wait_time)
    except ValueError as e:
        logging.error(f"Error: Could not build prompt for task {task}: {e}")
        progress_bar.update(samples)
    finally:
        logger.removeHandler(handler)
        handler.close()
    