import logging
import os
import subprocess
from typing import List

def execute_command(command: List[str], **kwargs) -> int:
    cwd = kwargs["cwd"] if "cwd" in kwargs else os.getcwd()
    output_dir = kwargs["output_dir"] if "output_dir" in kwargs else "."
    shell = kwargs["shell"] if "shell" in kwargs else False
    stdout = open(output_dir + "/" + kwargs["stdout"], 'w') if "stdout" in kwargs else None
    stderr = open(output_dir + "/" + kwargs["stderr"], 'w') if "stderr" in kwargs else None
    logging.debug(f'Executing "{" ".join(map(str, command))}" on directory "{cwd}"')
    if stdout:
        logging.debug(f'Standard output redirected to "{stdout.name}"')
    if stderr:
        logging.debug(f'Standard error redirected to "{stderr.name}"')

    ret_code = subprocess.call(command, cwd=cwd, stdout=stdout, stderr=stderr, shell=shell)

    if stdout:
        stdout.close()
    if stdout is not None and os.path.getsize(stdout.name) == 0:  # Delete error log if empty
        os.remove(stdout.name)
    if stderr:
        stderr.close()
    if stderr is not None and os.path.getsize(stderr.name) == 0:  # Delete error log if empty
        os.remove(stderr.name)

    return ret_code

def get_next_config(starting_blocks: int = 4,
                    max_blocks: int = 1,
                    out_folder: str = ".",
                    starting_instance_id: int = 1,
                    max_instance_id: int = 100,
                    seed: int = 42):
    instance_id = starting_instance_id
    step_block = float(max_blocks-starting_blocks) / float(1+max_instance_id-instance_id)
    while instance_id <= max_instance_id:
        blocks = int(starting_blocks + step_block * (instance_id - starting_instance_id))
        print(f"id={instance_id}; b={blocks}; seed={seed}")
        yield f"python blocksworld.py -b {blocks} -out {out_folder} -id {instance_id} --seed {seed}"
        # Update input values for the next instance
        instance_id += 1
        seed += 1


def main():
    # although most of easy cases are quickly solved by LAMA, there are some that are still too difficult
    # starting_blocks = [5, 5, 95, 160]
    # max_blocks = [90, 90, 150, 500]
    starting_blocks = [5, 5, 35, 160]
    max_blocks = [30, 30, 150, 500]
    output_folders = ["training/easy", "testing/easy", "testing/medium", "testing/hard"]
    init_ids = [15, 1, 1, 1]  # 14 base cases
    max_ids = [99, 30, 30, 30]
    seeds = [42, 1007, 1007, 1007]
    for experiment in range(4):
        for command in get_next_config(
                starting_blocks=starting_blocks[experiment],
                max_blocks=max_blocks[experiment],
                out_folder=output_folders[experiment],
                starting_instance_id=init_ids[experiment],
                max_instance_id=max_ids[experiment],
                seed=seeds[experiment]):
            ret_code = execute_command(command=command.split())
            logging.info(f"Executed command={command}; result={ret_code}")

    # Copy base cases
    command = "cp base_cases/* training/easy/"
    ret_code = execute_command(command=command, shell=True)
    logging.info(f"Executed command={command}; result={ret_code}")


if __name__ == "__main__":
    main()
