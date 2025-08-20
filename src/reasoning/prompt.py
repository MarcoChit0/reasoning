from reasoning.task import Domain, Instance, Task
from reasoning.utils import from_pyperplan, sort_landmarks
from string import Template
import random

storage_domain : Domain = Domain(name="storage", path="data/examples/storage/domain.pddl")
storage_instance : Instance = Instance(name="p01", path="data/examples/storage/instances/p01.pddl")
storage_example : Task = Task(domain=storage_domain, instance=storage_instance)

rover_domain : Domain = Domain(name="rover", path="data/examples/rover/domain.pddl")
rover_instance : Instance = Instance(name="p01", path="data/examples/rover/instances/p01.pddl")
rover_example : Task = Task(domain=rover_domain, instance=rover_instance)

class PromptBuilder:
    def __init__(self, template: str, tag:str, examples:list[Task] = [storage_example, rover_example], **kwargs):
        self.template = template
        self.tag = tag
        self.examples = examples
        self.metadata : dict[Task, dict[any, any]] = {}
        self.data : dict[Task, dict[any, any]] = {}
        self.__dict__.update(kwargs)

    def build(self, task: Task) -> str:
        self.process_task(task, is_example=False)
        for ex in self.examples:
            self.process_task(ex, is_example=True)
        examples_str = '\n\n'.join(
            [self.example_template.substitute(self.data[ex]) for ex in self.examples]
        )
        return f"""{self.description_template.substitute(**self.data[task])}

{self.problem_template.substitute(**self.data[task])}

{examples_str}

{self.checklist}"""

    def get_metadata(self, task):
        return self.metadata.get(task, {})

    def process_task(self, task: Task, is_example: bool) -> None:
        if not task in self.data:
            data = {
                "name": task.domain.name,
                "domain": task.domain.read(),
                "instance": task.instance.read()
            }
            if is_example:
                plan : list[str] = from_pyperplan(task, "plan")
                if not plan:
                    raise RuntimeError(f"Failed to get plan for example task {task}")
                data["plan"] = "\n".join(plan)
            self.data[task] = data
        if task not in self.metadata:
            self.metadata[task] = {
                "template" : self.template
            }

    @property
    def description_template(self) -> Template:
        return Template("""<problem-description>
You are a highly skilled professor in AI planning. Your task is to generate a plan for a PDDL instance from the domain <domain>$name</domain>. You will be given the PDDL domain file and the PDDL instance file, and you need to return the plan between the tags <plan> and </plan>. You will receive two examples to help you in generating the plan.
</problem-description>""")

    @property
    def problem_template(self) -> Template:
        return Template("""This is the PDDL domain file of the $name domain:
<domain-file>
$domain
</domain-file>

This is the PDDL instance file, for which you need to generate a plan:
<instance-file>
$instance
</instance-file>""")

    @property
    def example_template(self) -> Template:
        return Template("""This is the PDDL domain file of another domain, called $name, which serves as an example:
<domain-file-$name-example>
$domain
</domain-file-$name-example>

This is an example of a PDDL instance file from the $name domain:
<instance-file-$name-example>
$instance
</instance-file-$name-example>

This is a plan for the $name instance above:
<plan-$name-example>
$plan
</plan-$name-example>""")

    @property
    def checklist(self) -> str:
        return """Provide only the plan for the given instance. Here is a checklist to help you with your problem:
<checklist>
1) The plan must be in the same format as the examples above.
2) The plan should be preceded by the <plan> tag and should be followed by the </plan> tag.
3) The actions in the plan must be from the set of actions in the domain described above, that is, they must use the same name and the same number of parameters as one of the action schemas.
4) The plan must be valid, that is, each action must be applicable in the state it is applied, and the plan must end in a goal state.
</checklist>"""


pddl_prompt_builder = PromptBuilder(template="pddl", tag="-")

class LandmarksPromptBuilder(PromptBuilder):
    def __init__(self, template: str, tag: str, ordered:bool, explicit:bool, **kwargs):
        self.ordered = ordered
        self.explicit = explicit
        super().__init__(template, tag, **kwargs)
        if self.explicit and not self.ordered:
            raise ValueError("For using expliciting landmark order, they should be ordered")
    @property
    def description_template(self) -> Template:
        if self.explicit:
            order = """The action landmarks are provided in a partial order; this means that each landmark earlier in the list must appear before in the plan than other landmarks later in the list. 
Note that there could be other actions that must appear between landmarks in the plan. Also note that the order only needs to be respected for the first appearance of each landmark in the plan.
Every valid plan must include all action landmarks at some point during execution."""
        else:
            order = """Note that the action landmarks are provided in arbitrary order and do not necessarily reflect the order in which they must appear in the plan. 
However, every valid plan must include all action landmarks at some point during execution."""

        return Template(f"""<problem-description-with-landmarks>
You are a highly skilled professor in AI planning. Your task is to generate a plan for a PDDL instance from the domain <domain>$name</domain>. 
You will be given the PDDL domain file, the PDDL instance file, and the set of action landmarks extracted from the delete relaxation of the instance. 
Action landmarks are actions that must be part of any valid plan for the task. 
Since the action landmarks are extracted from the delete relaxation of the instance, they represent a subset of the action landmarks of the instance.
{order}
You need to return the plan between the tags <plan> and </plan>. You will receive two examples to help you in generating the plan.
</problem-description-with-landmarks>""")
        

    @property
    def problem_template(self) -> Template:
        return Template("""This is the PDDL domain file of the $name domain:
<domain-file>
$domain
</domain-file>

This is the PDDL instance file, for which you need to generate a plan:
<instance-file>
$instance
</instance-file>

This is a set of action landmarks for the instance you need to generate a plan for:
<action-landmarks-set>
$action_landmarks
</action-landmarks-set>""")

    @property
    def example_template(self) -> Template:
        return Template("""This is the PDDL domain file of another domain, called $name, which serves as an example:
<domain-file-$name-example>
$domain
</domain-file-$name-example>

This is an example of a PDDL instance file from the $name domain:
<instance-file-$name-example>
$instance
</instance-file-$name-example>

This is a set of action landmarks for the $name instance above:
<action-landmarks-set-$name-example>
$action_landmarks
</action-landmarks-set-$name-example>

This is a plan for the $name instance above:
<plan-$name-example>
$plan
</plan-$name-example>""")
    
    def process_task(self, task: Task, is_example: bool) -> None:
        if not task in self.data:
            super().process_task(task, is_example)
            landmarks = from_pyperplan(task, "landmark")
            if self.ordered:
                try:
                    landmarks = sort_landmarks(task, landmarks)
                except RuntimeError as e:
                    raise RuntimeError(f"Failed to sort action landmarks: {e}")            
            else:
                random.seed(42)
                random.shuffle(landmarks)
            self.data[task]["action_landmarks"] = "\n".join(landmarks) if len(landmarks) > 0 else ""
            self.metadata[task]["action_landmarks"] = self.data[task]["action_landmarks"]
            self.metadata[task]["num_action_landmarks"] = len(landmarks)

nonordered_landmarks_prompt_builder = LandmarksPromptBuilder(template="nonordered_landmarks", tag="Non-Ordered Landmarks", ordered=False, explicit=False)

ordered_landmarks_omitted_prompt_builder = LandmarksPromptBuilder(template="ordered_landmarks_omitted", tag="Ordered Landmarks (Omitted)", ordered=True, explicit=False)

ordered_landmarks_explicit_prompt_builder = LandmarksPromptBuilder(template="ordered_landmarks_explicit", tag="Ordered Landmarks", ordered=True, explicit=True)

class DeleteRelaxedPlanPromptBuilder(PromptBuilder):
    @property
    def description_template(self) -> Template:
        return Template("""<problem-description-with-delete-relaxed-plan>
You are a highly skilled professor in AI planning. Your task is to generate a plan for a PDDL instance from the domain <domain>$name</domain>. 
You will be given the PDDL domain file, the PDDL instance file, and a delete-relaxed plan for the PDDL instance.
The delete-relaxed plan is generated by ignoring all delete effects in the PDDL domain and generating a plan for the PDDL instance with this delete-relaxed domain.
That delete-relaxed plan may be invalid for the original domain; but you may use the delete-relaxed plan to help you in generating the plan.
You need to return the plan between the tags <plan> and </plan>. You will receive two examples to help you in generating the plan.
</problem-description-with-delete-relaxed-plan>""")

    @property
    def problem_template(self) -> Template:
        return Template("""This is the PDDL domain file of the $name domain:
<domain-file>
$domain
</domain-file>

This is the PDDL instance file, for which you need to generate a plan:
<instance-file>
$instance
</instance-file>

This is a delete-relaxed plan for the instance you need to generate a plan for:
<delete-relaxed-plan>
$delete_relaxed_plan
</delete-relaxed-plan>""")
    
    @property
    def example_template(self) -> Template:
        return Template("""This is the PDDL domain file of another domain, called $name, which serves as an example:
<domain-file-$name-example>
$domain
</domain-file-$name-example>

This is an example of a PDDL instance file from the $name domain:
<instance-file-$name-example>
$instance
</instance-file-$name-example>

This is a delete-relaxed plan for the $name instance above:
<delete-relaxed-plan-$name-example>
$delete_relaxed_plan
</delete-relaxed-plan-$name-example>

This is a plan for the $name instance above:
<plan-$name-example>
$plan
</plan-$name-example>""")
    
    def process_task(self, task: Task, is_example: bool) -> None:
        if not task in self.data:
            _ = super().process_task(task, is_example)
            delete_relaxed_plan = from_pyperplan(task, "delete_relaxed_plan")
            self.data[task]["delete_relaxed_plan"] = "\n".join(delete_relaxed_plan) if len(delete_relaxed_plan) > 0 else ""
            self.metadata[task]["delete_relaxed_plan"] = self.data[task]["delete_relaxed_plan"]
            self.metadata[task]["delete_relaxed_plan_length"] = len(delete_relaxed_plan)

delete_relaxed_plan_prompt_builder = DeleteRelaxedPlanPromptBuilder(template="delete_relaxed_plan", tag="Delete Relaxation")

def get_prompt_builder(template: str) -> PromptBuilder:
    available_prompt_builders = [
        pddl_prompt_builder,
        nonordered_landmarks_prompt_builder,
        ordered_landmarks_omitted_prompt_builder,
        ordered_landmarks_explicit_prompt_builder,
        delete_relaxed_plan_prompt_builder
    ]
    for prompt_builder in available_prompt_builders:
        if prompt_builder.template == template:
            return prompt_builder
    raise ValueError(f"No prompt builder found for template: {template}")

def get_tag(template: str) -> str:
    return get_prompt_builder(template).tag