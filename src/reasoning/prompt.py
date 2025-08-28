from __future__ import annotations
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
    TEMPLATE_PATTERN = r"([\w\s\d_]+)(?:\[([\w\s\d_+\(<>\)=]+)\])?"
    def __init__(self, template: str, tag:str, examples:list[Task] = [storage_example, rover_example], **template_kwargs):
        self.template = template
        self.tag = tag
        self.examples = examples
        self.metadata : dict[Task, dict[any, any]] = {}
        self.data : dict[Task, dict[any, any]] = {}
        self.template_kwargs = template_kwargs

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
    
    def get_template(self):
        template = self.template
        kwargs = self.get_template_kwargs()
        if kwargs:
            template += f"[{kwargs}]"
        return template

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
                "template" : self.get_template(),
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

    def parse_template(self, template: str) -> tuple[str | None, dict[str, str]]:
        match = re.match(self.TEMPLATE_PATTERN, template)
        if match:
            temp = match.group(1)
            temp_kwargs_str = match.group(2)
            temp_kwargs_data = {}
            if temp_kwargs_str:
                for item in temp_kwargs_str.split("+"):
                    not_fact_pattern = r"not\(([\w\s\d_]+)\)"
                    map_pattern = r"\(([\w\s\d_]+)=([\w\s\d_]+)\)"
                    fact_pattern = r"([\w\s\d_]+)"
                    if not_match := re.match(not_fact_pattern, item):
                        key = not_match.group(1)
                        temp_kwargs_data[key] = False
                    elif map_match := re.match(map_pattern, item):
                        key, value = map_match.groups()
                        temp_kwargs_data[key] = value
                    elif fact_match := re.match(fact_pattern, item):
                        key = fact_match.group(1)
                        temp_kwargs_data[key] = True
                    else:
                        raise ValueError(f"Invalid template item: {item}")
            return temp, temp_kwargs_data
        return None, {}

    def set_template_kwargs(self, template: str) -> PromptBuilder | None:
        if not self.has_matching_template(template):
            return None
        _, kwargs = self.parse_template(template)
        self.template_kwargs = kwargs
        return self

    def has_matching_template(self, template: str) -> bool:
        temp, _ = self.parse_template(template)
        if temp:
            return temp == self.template
        return False
    
    def get_tag(self):
        tag = self.tag
        kwargs = self.get_template_kwargs()
        if kwargs:
            tag += f" [{kwargs}]"
        return tag
    
    def get_template_kwargs(self):
        kwargs_str = ""
        for key, value in self.template_kwargs.items():
            if isinstance(value, bool):
                if value:
                    kwargs_str += f"+{key}"
                else:
                    kwargs_str += f"+not({key})"
            else:
                kwargs_str += f"+({key}={value})"
        if kwargs_str:
            kwargs_str = kwargs_str[1:]
        return kwargs_str

import re
class LandmarksPromptBuilder(PromptBuilder):
    def __init__(
            self, 
            template: str, 
            tag: str, 
            ordered:bool, 
            description_style: str | None = None, 
            order_style:str | None = None,
            **kwargs):
        self.ordered : bool = ordered
        self.order_style : str | None = order_style
        self.description_style : str | None = description_style
        super().__init__(template, tag, **kwargs)
        if not self.ordered and self.order_style and self.order_style == "explicit":
            raise ValueError("For using expliciting landmark order, they should be ordered")

    @property
    def description_template(self) -> Template:
        order = """Note that the action landmarks are provided in arbitrary order and do not necessarily reflect the order in which they must appear in the plan."""
        description = """Action landmarks are actions that must be part of any valid plan for the instance.
Since the action landmarks are extracted from the delete relaxation of the instance, they represent a subset of the action landmarks of the instance."""
        tips = []
        if self.order_style:
            if self.order_style == "explicit":
                order = """The action landmarks are provided in a partial order; this means that each landmark earlier in the list must appear before in the plan than other landmarks later in the list."""
            elif self.order_style == "exact":
                order = """The action landmarks are provided in the exact order in which they must appear in the plan."""
            elif self.order_style == "feasible":
                order = """The action landmarks are provided in a feasible order; this means that there is at least one valid plan that could be built following the action landmarks order."""
        if self.template_kwargs:
            for key, value in self.template_kwargs.items():
                if key == "unique":
                    tips.append("Note that this ordering is not necessarily unique; this means that there could exist other valid plans that could be built following the action landmarks from another ordering.")
                elif key == "optimal":
                    tips.append("Note that this ordering is not necessarily optimal; this means that there could exist more efficient plans or optimal plans that could be built following the action landmarks from another ordering.")
                elif key == "other_actions":
                    tips.append("Note that there could be other actions that must appear between landmarks in the plan.")
                elif key == "first_appearance":
                    tips.append("Note that the order only needs to be respected for the first appearance of each landmark in the plan.")
                elif key == "use_all":
                    tips.append("Note that every valid plan must include all action landmarks at some point during execution.")
        template = f"""<problem-description-with-landmarks>
You are a highly skilled professor in AI planning. Your task is to generate a plan for a PDDL instance from the domain <domain>$name</domain>.
You will be given the PDDL domain file, the PDDL instance file, and the set of action landmarks extracted from the delete relaxation of the instance.\n"""
        if description:
            template += f"{description}\n"
        if order:
            template += f"{order}\n"
        if len(tips) > 0:
            tips_str = '\n'.join(tips)
            template += f"{tips_str}\n"
        template += f"""You need to return the plan between the tags <plan> and </plan>.
You will receive two examples to help you in generating the plan.
</problem-description-with-landmarks>"""
        return Template(template)
        

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

AVAILABLE_PROMPT_BUILDERS : list[PromptBuilder] = [
    PromptBuilder(template="pddl", tag="-"),
    LandmarksPromptBuilder(template="nonordered_landmarks", tag="Non-Ordered Landmarks", ordered=False),
    LandmarksPromptBuilder(template="ordered_landmarks_omitted", tag="Ordered Landmarks Omitted", ordered=True),
    LandmarksPromptBuilder(template="ordered_landmarks_explicit", tag="Ordered Landmarks Explicit", ordered=True, order_style="explicit"),
    LandmarksPromptBuilder(template="ordered_landmarks_exact", tag="Ordered Landmarks Exact", ordered=True, order_style="exact"),
    LandmarksPromptBuilder(template="ordered_landmarks_feasible", tag="Ordered Landmarks Feasible", ordered=True, order_style="feasible"),
    DeleteRelaxedPlanPromptBuilder(template="delete_relaxed_plan", tag="Delete Relaxation"),
]

def get_prompt_builder(template: str) -> PromptBuilder:
    global AVAILABLE_PROMPT_BUILDERS
    for pb in AVAILABLE_PROMPT_BUILDERS:
        if pb.has_matching_template(template):
            pb.set_template_kwargs(template)
            return pb
    return None

def get_tag(template: str) -> str:
    try:
        pb = get_prompt_builder(template)
        return pb.get_tag()
    except ValueError:
        raise ValueError(f"No tag found for template: {template}")