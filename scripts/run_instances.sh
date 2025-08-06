#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
BENCHMARKS_DIR="data/benchmarks"
SOLUTIONS_DIR="${BENCHMARKS_DIR}/solutions"
CSV_FILE="results.csv"
PLANNER_SCRIPT="res/pyperplan/pyperplan"
TIMEOUT_SECONDS=1800 # 30 minutes
MEMORY_LIMIT_KB=$((24 * 1024 * 1024)) # 24 GB in Kilobytes for ulimit

# --- Script Start ---

# Create the main solutions directory
mkdir -p "$SOLUTIONS_DIR"

# Initialize CSV file with a header
echo "domain,instance,steps" > "$CSV_FILE"

# Loop through each domain directory in the benchmarks directory
for domain_path in "$BENCHMARKS_DIR"/*; do
    # Ensure it's a directory
    if [ ! -d "$domain_path" ]; then
        continue
    fi

    domain=$(basename "$domain_path")

    # Skip the solutions directory itself
    if [ "$domain" == "solutions" ]; then
        continue
    fi

    INSTANCES_PATH="${domain_path}/instances"
    DOMAIN_PDDL="${domain_path}/domain.pddl"

    # Check if the required 'instances' subdir and 'domain.pddl' file exist
    if [ ! -d "$INSTANCES_PATH" ] || [ ! -f "$DOMAIN_PDDL" ]; then
        echo "Skipping domain '$domain': missing 'instances' directory or 'domain.pddl'"
        continue
    fi

    # Create a specific directory for this domain's solutions
    DOMAIN_SOLUTION_DIR="${SOLUTIONS_DIR}/${domain}"
    mkdir -p "$DOMAIN_SOLUTION_DIR"

    # Use 'find' to recursively locate all .pddl files, similar to os.walk
    find "$INSTANCES_PATH" -type f -name "*.pddl" | while read -r instance_file; do
        echo "Processing ${instance_file} in domain ${domain}"
        
        # Define the output file name that the planner will create
        output_file="${instance_file}.soln"
        instance_basename=$(basename "$instance_file")

        # Run the planner in a subshell to contain the 'ulimit' command.
        # This prevents the memory limit from affecting the main script.
        # The 'timeout' command handles the execution time limit.
        (
            ulimit -v "$MEMORY_LIMIT_KB"
            timeout "$TIMEOUT_SECONDS" python "$PLANNER_SCRIPT" "$DOMAIN_PDDL" "$instance_file" -s astar -H hff
        ) || {
            # The subshell will exit with a non-zero status on error or timeout.
            # We check the timeout exit code specifically.
            if [ $? -eq 124 ]; then
                echo "Timeout expired for instance $instance_file"
            else
                # Other errors are noted, but we continue, checking for a solution file just in case.
                echo "Planner exited with an error for instance $instance_file"
            fi
        }

        # Check if a solution file was created
        if [ -f "$output_file" ]; then
            # Count the lines in the solution file (number of steps)
            # 'wc -l' outputs "COUNT FILENAME", so we pipe to awk to get just the count.
            line_count=$(wc -l < "$output_file" | awk '{print $1}')
            
            echo -e "\t-> Solution found with ${line_count} steps."

            # Append the result to the CSV file
            echo "${domain},${instance_basename},${line_count}" >> "$CSV_FILE"

            # Move the solution file to the organized solutions directory
            mv "$output_file" "$DOMAIN_SOLUTION_DIR/"
        else
            echo -e "\t-> No solution found."
        fi
        echo # Add a newline for better readability
    done
done

echo "Benchmark processing complete. Results are in $CSV_FILE"