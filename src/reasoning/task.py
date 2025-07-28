import threading

lock = threading.Lock()

def read_pddl(pddl_path : str) -> str:
    with lock:
        with open(pddl_path, "r", encoding='utf-8') as f:
            content = f.read()
            return "\n".join([line for line in content.splitlines() if not line.strip().startswith(";") or line.strip() == ""])

class PDDLResource:
    def __init__(self, name : str, path : str):
        self.name = name
        self.path = path
    
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
    def __init__(self, name : str, path : str, type : str):
        super().__init__(name, path)
        self.type = type

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

    domain_dir = os.path.join(settings.RAW_DIR, domain)
    domain_path = os.path.join(domain_dir, domain_info['path'])
    assert os.path.exists(domain_path), f"Domain file '{domain_path}' does not exist."
    
    _domain = Domain(name=domain, path=domain_path)
    tasks : list[Task] = []

    for inst_type in domain_info.get('instances', {}):
        if instance_type and inst_type != instance_type:
            continue

        if not domain_info['instances'][inst_type].get('dir', None):
            raise ValueError(f"Instance directory for type '{inst_type}' not specified in structure.")
        
        instance_dir = os.path.join(domain_dir, domain_info['instances'][inst_type]['dir'])
        assert os.path.exists(instance_dir), f"Instance directory '{instance_dir}' does not exist in domain '{domain}'."

        regex_pattern = domain_info['instances'][inst_type].get('regex', None)
        assert regex_pattern, f"Regex pattern for instances of type '{inst_type}' not specified in structure."


        for file in os.listdir(instance_dir):
            if not re.match(regex_pattern, file):
                continue

            instance_path = os.path.join(instance_dir, file)
            if not os.path.isfile(instance_path):
                continue

            _instance = Instance(
                name=re.match(regex_pattern, file).group(1),
                path=instance_path,
                type=inst_type
            )
            tasks.append(Task(_domain, _instance))

    return tasks