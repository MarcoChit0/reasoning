import threading

lock = threading.Lock()

def read_pddl(pddl_path : str) -> str:
    with lock:
        with open(pddl_path, "r", encoding='utf-8') as f:
            content = f.read()
            return "\n".join([line for line in content.splitlines() if not line.strip().startswith(";") or line.strip() == ""])

class Task:
    def __init__(self, domain : str, domain_path : str, instance : str, instance_path : str, instance_type : str):
        self.domain : str = domain
        self.domain_path : str = domain_path
        self.instance : str = instance
        self.instance_path : str = instance_path
        self.instance_type : str = instance_type

    def __str__(self):
        return f"Task(domain={self.domain_path}, instance={self.instance_path})"

    def __eq__(self, value):
        if not isinstance(value, Task):
            return False
        return (self.domain_path == value.domain_path and
                self.instance_path == value.instance_path)

    def __hash__(self):
        return hash((self.domain_path, self.instance_path))

    def __lt__(self, other):
        if not isinstance(other, Task):
            return NotImplemented
        return (self.domain_path, self.instance_path) < (other.domain_path, other.instance_path)
    
    def read_domain(self) -> str:
        return read_pddl(self.domain_path)

    def read_instance(self) -> str:
        return read_pddl(self.instance_path)

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

    tasks : list[Task] = []
    print(domain_info.get('instances', {}))
    for inst_type in domain_info.get('instances', {}):
        print(inst_type)
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

            instance = re.match(regex_pattern, file).group(1)
            tasks.append(Task(
                domain=domain,
                domain_path=domain_path,
                instance=instance,
                instance_path=instance_path,
                instance_type=inst_type
            ))

    return tasks