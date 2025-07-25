from reasoning.task import Task

def build_prompt(task : Task, template : str):
    if template == "pddl":
        from reasoning.templates.pddl import PDDL_TEMPLATE

        name = task.domain
        domain = task.read_domain()
        instance = task.read_instance()
        return PDDL_TEMPLATE.substitute(name=name, domain=domain, instance=instance)

    else:
        raise ValueError(f"Unknown template value: {template}")