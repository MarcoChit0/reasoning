#!/bin/bash

# Define the grid sizes and the number of instances per grid size
grid_sizes=(4 6 8 10 12)
conf_blocks=4
instances_per_grid=4

# Get the directory of the script
script_dir=$(dirname "$(readlink -f "$0")")
instances_dir="$script_dir/instances"
tetris_path="$script_dir/generator.py"

# Create the instances directory if it doesn't exist
mkdir -p "$instances_dir"

inst=1
# Loop through each grid size
for grid_size in "${grid_sizes[@]}"; do
    grid_dir="$instances_dir/${grid_size}-grid"
    mkdir -p "$grid_dir"
    
    created_instances=0
    seed=0
    
    # Loop until the desired number of instances are created for the current grid size
    while [ $created_instances -lt $instances_per_grid ]; do
        seed=$((seed + 1))
        instance_name=$(printf "p%02d.pddl" $inst)
        instance_path="$grid_dir/$instance_name"
        solution_path="$instance_path.soln"

        # Generate the Tetris instance
        python "$tetris_path" "$grid_size" "$conf_blocks" "$seed" > "$instance_path"

        # Try to solve with Pyperplan with a 5-minute timeout and 24GB memory limit
        (
            ulimit -v 25165824
            timeout 300s python res/pyperplan/pyperplan -s gbf -H lmcut data/benchmarks/tetris/domain.pddl $instance_path
        )

        # Check if a solution file was created
        if [ -f "$solution_path" ]; then
            echo "Solution found for instance $instance_name with seed $seed"
            created_instances=$((created_instances + 1))
            inst=$((inst + 1))
        else
            echo "No solution found for instance $instance_name with seed $seed (or it timed out)"
            rm "$instance_path"
        fi
    done
done