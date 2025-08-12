from datetime import time
import yaml
import tqdm
import os
import reasoning.models as models
from reasoning.task import Task, get_tasks
from reasoning.prompt import build_prompt
from reasoning.utils import from_config
import logging
from reasoning.settings import EXPERIMENTS_DIR

def generate(model: models.Model, tasks: list[Task], template: str, samples: int, experiment: str, model_dir: str, **kwargs):
    for task in tqdm.tqdm(tasks, desc="Generating content", unit="task"):
        dir_path = os.path.join(
            EXPERIMENTS_DIR,
            experiment,
            model_dir,
            template,
            task.domain.name,
            *task.instance.subdirs,
        )
        os.makedirs(dir_path, exist_ok=True)
        log_file = os.path.join(dir_path, f"{task.instance.name}.log")
        if os.path.exists(log_file):
            continue

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler(log_file, mode='w')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        try:
            logging.info(f"Processing task: {task}")
            logging.info(f"Using model: {model.name}")
            logging.info(f"Generation parameters: {kwargs}")
            prompt = build_prompt(task, template, logger)
            for i in range(samples):
                logging.info(f"Sample: {i + 1}.")
                success = False
                sample = "\n<sample>\n"
                try:
                    response = model.generate_response(prompt, **kwargs)
                    sample += f"<response>\n{response['response']}\n</response>\n"
                    sample += f"<metadata>\n{str(response['metadata'])}\n</metadata>\n"
                    success = True
                except RuntimeError as e:
                    sample += f"<error>\n{str(e)}\n</error>\n"
                finally:
                    sample += "</sample>\n"
                    if success:
                        logging.info(sample)
                    else:
                        logging.error(sample)
                    
        except ValueError as e:
            logging.error(f"Error: Could not build prompt for task {task}: {e}")
        finally:
            logger.removeHandler(handler)
            handler.close()

if __name__ == "__main__":
    experiment = "pddl-vs-new-landmarks-on-new-instances"
    samples = 1
    templates = ["pddl", "new_landmark"]
    domains = ["blocksworld", "logistics", "miconic"]
    # domains = ["blocksworld"]
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

