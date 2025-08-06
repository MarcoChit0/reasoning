from datetime import time
import dotenv
import yaml
import tqdm
import os
from reasoning.model import GoogleModel
from reasoning.task import Task, get_tasks
from reasoning.prompt import build_prompt
import logging
import numpy as np
import time
from reasoning.settings import EXPERIMENTS_DIR
dotenv.load_dotenv()
api_key = dotenv.get_key(dotenv.find_dotenv(), "GOOGLE_API_KEY")

def generate(config_path: str, domain: str, template: str, instances: int, samples: int, experiment: str = time.time()):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    model_name = config.get("model_name", None)
    assert model_name is not None, "Model name must be specified in the configuration file."
    model = GoogleModel(
        model_name=model_name,
        api_key=api_key
    )
    wait_time = config.get("wait_time", 0)
    generation_config = config.get("generation_config", {})
    config_name = config_path.split('/')[-1].split('.')[0].strip()

    tasks : list[Task] = get_tasks(domain)
    print(f"Found {len(tasks)} tasks for domain '{domain}'.")

    # Set random seed for reproducibility
    np.random.seed(42)
    # Randomly select instances number of tasks
    indices = np.random.choice(len(tasks), min(instances, len(tasks)), replace=False)
    tasks = [tasks[i] for i in indices]

    already_generated_instances = [f.split(".")[0] for f in os.listdir(dir_path) if f.endswith(".log")]
    print(f"Already generated instances: {len(already_generated_instances)}")

    tasks = [task for task in tasks if task.instance.name not in already_generated_instances]
    print(f"Remaining tasks to generate: {len(tasks)}")

    progress_bar = tqdm.tqdm(total=len(tasks) * samples, desc="Generating content", unit="sample")

    for task in tasks:
        dir_path = os.path.join(
            EXPERIMENTS_DIR,
            experiment,
            config_name,
            template,
            domain,
            *task.instance.subdirs,
        )
        os.makedirs(dir_path, exist_ok=True)

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        log_file = os.path.join(dir_path, f"{task.instance.name}.log")
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

if __name__ == "__main__":
    experiment = "many-models"
    samples = 1
    templates = ["pddl", "landmark"]
    instances = 20
    domains = ["logistics", "blocksworld", "spanner", "miconic"]
    config_paths = [
        "src/configs/gemini-thinking.yaml",
    ]

    for config_path in config_paths:
        for template in templates:
            for domain in domains:
                print(f"Experiment '{experiment}': generating content for domain '{domain}', template '{template}', using config '{config_path}'.")
                generate(
                    config_path=config_path,
                    domain=domain,
                    template=template,
                    instances=instances,
                    samples=samples,
                    experiment=experiment
                )