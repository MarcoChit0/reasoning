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
    PATTERN = r"p(\d+)\.pddl"
    def __init__(self, name : str, path : str):
        super().__init__(name, path)
        filename = os.path.basename(path)
        match = re.match(self.PATTERN, filename)
        if match:
            self.id : int = int(match.group(1))
        else:
            self.id : int = 0 
        path_parts = self.path.split(os.sep)
        instances_idx = path_parts.index('instances')
        subdirectory_parts = path_parts[instances_idx + 1:-1]
        self.subdirs : list[str] = subdirectory_parts if subdirectory_parts else []

    def __lt__(self, other):
        if not isinstance(other, Instance):
            return NotImplemented
        return self.id < other.id

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

from reasoning import settings
import os
import re 
from reasoning import settings
import os
import re 

def get_tasks(domain : str)-> list[Task]:
    domain_dir_path = os.path.join(settings.BENCHMARKS_DIR, domain)
    if not os.path.isdir(domain_dir_path):
        raise ValueError(f"Domain directory '{domain_dir_path}' does not exist.")
    domain_path = os.path.join(domain_dir_path, "domain.pddl")
    if not os.path.isfile(domain_path):
        raise ValueError(f"Domain file '{domain_path}' does not exist.")
    d = Domain(
        name=domain,
        path=domain_path
    )
    instance_dir_path = os.path.join(domain_dir_path, "instances")
    if not os.path.isdir(instance_dir_path):
        raise ValueError(f"Instance directory '{instance_dir_path}' does not exist.")
    tasks = []
    for root, dirs, files in os.walk(instance_dir_path):
        for instance_file in files:
            if not instance_file.endswith('.pddl'):
                continue
            instance_path = os.path.join(root, instance_file)
            i = Instance(
                name=instance_file.replace('.pddl', '').strip(),
                path=instance_path
            )
            tasks.append(Task(d, i))
    return tasks