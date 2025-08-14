from reasoning.task import Task
from reasoning.utils import from_pyperplan
from string import Template
from typing import Optional

def build_prompt(task : Task, template : str) -> dict[str, str]:
    metadata = {"template": template}
    if template == "pddl":
        from reasoning.templates.pddl import PDDL_TEMPLATE

        name = task.domain.name
        domain = task.domain.read()
        instance = task.instance.read()
        prompt = PDDL_TEMPLATE.substitute(name=name, domain=domain, instance=instance)
    elif template in ["landmark", "new_landmark", "random_landmark", "random_new_landmark"]:
        template : Optional[Template]
        rand = False
        if "random" in template:
            template = template.replace("random_", "")
            rand = True
        if template == "landmark":
            from reasoning.templates.landmark import LANDMARK_TEMPLATE
            template = LANDMARK_TEMPLATE
        else:
            from reasoning.templates.new_landmark import NEW_LANDMARK_TEMPLATE
            template = NEW_LANDMARK_TEMPLATE
        assert template is not None, "Template must be defined for landmark generation"
        try:
            action_landmarks = from_pyperplan(task, "landmark")
            if rand:
                import random
                random.seed(42)
                random.shuffle(action_landmarks)
            landmarks = "\n".join(action_landmarks) if len(action_landmarks) > 0 else ""
        except RuntimeError as e:
            raise RuntimeError(f"Failed to get action landmarks: {e}")
        
        name = task.domain.name
        domain = task.domain.read()
        instance = task.instance.read()
        prompt = template.substitute(name=name, domain=domain, instance=instance, landmarks=landmarks)
        metadata["action_landmarks"] = action_landmarks
        metadata["num_action_landmarks"] = len(action_landmarks)
    elif template == "sanity_check":
        from reasoning.templates.sanity_check import SANITY_CHECK_TEMPLATE, get_example_for_domain

        name = task.domain.name
        domain = task.domain.read()
        instance = task.instance.read()
        example_instance, example_plan = get_example_for_domain(name)
        prompt = SANITY_CHECK_TEMPLATE.substitute(name=name, domain=domain, instance=instance, example_instance=example_instance, example_plan=example_plan)
    elif template == "delete_relaxed_plan":
        name = task.domain.name
        domain = task.domain.read()
        instance = task.instance.read()
        delete_relaxed_plan = from_pyperplan(task, "delete_relaxed_plan")
        delete_relaxed_plan = "\n".join(delete_relaxed_plan) if len(delete_relaxed_plan) > 0 else ""
        from reasoning.templates.delete_relaxed_plan import DELETE_RELAXED_PLAN
        prompt = DELETE_RELAXED_PLAN.substitute(name=name, domain=domain, instance=instance, delete_relaxed_plan=delete_relaxed_plan)

    else:
        raise ValueError(f"Unknown template value: {template}")
    return {"prompt": prompt, "metadata": metadata}
