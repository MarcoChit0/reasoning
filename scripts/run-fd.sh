#!/bin/bash

# This script automates running the Fast Downward planner on a set of benchmarks.
# It iterates through domain directories, finds all problem instances,
# and runs the planner for each, saving the output to a corresponding solution file.

# --- Configuration ---
# Base directory where the PDDL benchmark domains are located.
BENCHMARKS_DIR="../reasoning/data/benchmarks"
# Base directory where the planner's solutions will be saved.
SOLUTIONS_DIR="../reasoning/data/solutions"
# The alias for the planner configuration to use.
PLANNER_ALIAS="lama-first"

# --- Main Script Logic ---

# Check if the benchmarks directory exists.
if [ ! -d "$BENCHMARKS_DIR" ]; then
    echo "Error: Benchmarks directory not found at ${BENCHMARKS_DIR}"
    exit 1
fi

# Loop through each domain directory in the benchmarks folder.
# The */ ensures we only match directories.
for domain_path in "$BENCHMARKS_DIR"/*/; do
    # Extract the domain name from its path (e.g., "blocksworld").
    domain=$(basename "$domain_path")
    echo "--- Processing domain: $domain ---"

    # Define the path to the domain's PDDL file.
    domain_file="${domain_path}domain.pddl"

    # Check if the domain file actually exists before proceeding.
    if [ ! -f "$domain_file" ]; then
        echo "Warning: No domain.pddl found for domain '$domain'. Skipping."
        continue
    fi

    # Create a corresponding directory in the solutions folder for the current domain.
    # The '-p' flag ensures that the command doesn't fail if the directory already exists.
    mkdir -p "${SOLUTIONS_DIR}/${domain}"

    # Find all instance files (ending in .pddl) within the domain's 'instances' subdirectory.
    # The 'find' command handles nested directories automatically.
    find "${domain_path}instances" -type f -name "*.pddl" | while read -r instance_file; do
        # Extract the instance filename from its full path (e.g., "p44.pddl").
        instance_name=$(basename "$instance_file")
        echo "Running planner on instance: $instance_name"

        # Define the full path for the output solution file.
        solution_file="${SOLUTIONS_DIR}/${domain}/${instance_name}.soln.dw"

        # Construct and execute the Fast Downward command.
        # The output (stdout) is appended to the solution file.
        ./fast-downward.py --alias "$PLANNER_ALIAS" "$domain_file" "$instance_file" >> "$solution_file"
    done
done

echo "--- All domains processed. ---"
