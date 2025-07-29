import threading

lock = threading.Lock()

class PDDLResource:
    def __init__(self, name : str, path : str):
        self.name : str = name
        self.path : str = path

    def __eq__(self, other):
        if not isinstance(other, PDDLResource):
            return False
        return self.path == other.path
    
    def __hash__(self):
        return hash(self.path)

    def __lt__(self, other):
        if not isinstance(other, PDDLResource):
            return NotImplemented
        return self.path < other.path

    def read(self) -> str:
        with lock:
            with open(self.path, "r", encoding='utf-8') as f:
                content = f.read()
                # Remove comments and empty lines
                _content = []
                for line in content.splitlines():
                    if line.strip().startswith(";") or line.strip() == "":
                        continue
                    _content.append(line.strip())
                return "\n".join(_content)
    
    def __str__(self):
        fields = ", ".join(f"{key}={value}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({fields})"

class Domain(PDDLResource):
    def __init__(self, name : str, path : str):
        super().__init__(name, path)

class Instance(PDDLResource):
    def __init__(self, name : str, path : str, id: int, type : str):
        super().__init__(name, path)
        self.type : str = type
        self.id : int = id
    
    def __lt__(self, other):
        if not isinstance(other, Instance):
            return NotImplemented
        return (self.type, self.id) < (other.type, other.id)

class Task:
    def __init__(self, domain : Domain, instance : Instance):
        self.domain : Domain = domain
        self.instance : Instance = instance

    def __str__(self):
        return "Task(domain={}, instance={})".format(self.domain.name, self.instance.name)

    def __eq__(self, other):
        if not isinstance(other, Task):
            return False
        return (self.domain == other.domain and
                self.instance == other.instance)

    def __hash__(self):
        return hash((self.domain, self.instance))

    def __lt__(self, other):
        if not isinstance(other, Task):
            return NotImplemented
        return (self.domain, self.instance) < (other.domain, other.instance)

from reasoning import settings
from typing import Optional
import os
import yaml
import re 

def get_tasks_from_raw(domain : str, instance_type : Optional[str] = None)-> list[Task]:
    with open(settings.STRUCTURE_FILE, 'r') as f:
        structure = yaml.safe_load(f)

    assert domain in structure, f"Domain '{domain}' not found in {settings.STRUCTURE_FILE}."
    domain_info = structure[domain]
    assert 'path' in domain_info, f"Path for domain '{domain}' not specified in structure."
    domain_path = domain_info['path']
    assert os.path.exists(domain_path), f"Domain file '{domain_path}' does not exist."
    
    _domain = Domain(name=domain, path=domain_path)
    tasks : list[Task] = []

    assert 'instances' in domain_info, f"Instances for domain '{domain}' not specified in structure."
    instances_info = domain_info['instances']
    assert instance_type in instances_info, f"Instance type '{instance_type}' not found in domain '{domain}'."

    assert "dir_path" in instances_info[instance_type], f"Directory path for instances of type '{instance_type}' not specified in structure."
    instance_dir = instances_info[instance_type]['dir_path']

    assert "regex" in instances_info[instance_type], f"Regex pattern for instances of type '{instance_type}' not specified in structure."
    regex_pattern = instances_info[instance_type]['regex']

    for file in os.listdir(instance_dir):
        if not re.match(regex_pattern, file):
            continue

        instance_path = os.path.join(instance_dir, file)
        if not os.path.isfile(instance_path):
            continue

        _instance = Instance(
            name=file.split('/')[-1].replace('.pddl', '').strip(),
            path=instance_path,
            id=int(re.match(regex_pattern, file).group(1)),
            type=instance_type
        )
        tasks.append(Task(_domain, _instance))

    return tasks