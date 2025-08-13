#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
BENCHMARKS_DIR="data/benchmarks"
SOLUTIONS_DIR="data/solutions"
CSV_FILE="results.csv"
PLANNER_SCRIPT="res/pyperplan/pyperplan"
TIMEOUT_SECONDS=1800 # 30 minutes
MEMORY_LIMIT_KB=$((24 * 1024 * 1024)) # 24 GB in Kilobytes for ulimit

# --- Script Start ---

# Create the main solutions directory
mkdir -p "$SOLUTIONS_DIR"

# Initialize CSV file with a header for the lmcut results
echo "domain,instance,steps" > "$CSV_FILE"

# Loop through each domain directory in the benchmarks directory
for domain_path in "$BENCHMARKS_DIR"/*; do
    # Ensure it's a directory
    if [ ! -d "$domain_path" ]; then
        continue
    fi

    domain=$(basename "$domain_path")

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

    # Use 'find' to recursively locate all .pddl files
    find "$INSTANCES_PATH" -type f -name "*.pddl" | while read -r instance_file; do
        echo "Processing ${instance_file} in domain ${domain}"
        instance_basename=$(basename "$instance_file")
        
        # --- 1. Run the existing planner with lmcut heuristic ---
        output_file="${instance_file}.soln"
        dest_output_file="${DOMAIN_SOLUTION_DIR}/$(basename "$output_file")"
        
        # Check if solution already exists
        if [ -f "$dest_output_file" ]; then
            line_count=$(wc -l < "$dest_output_file" | awk '{print $1}')
            echo -e "\t-> lmcut solution already exists with ${line_count} steps. Skipping."
            # Make sure the solution is already in the CSV
            if ! grep -q "${domain},${instance_basename},${line_count}" "$CSV_FILE"; then
                echo "${domain},${instance_basename},${line_count}" >> "$CSV_FILE"
            fi
        else
            (
                ulimit -v "$MEMORY_LIMIT_KB"
                timeout "$TIMEOUT_SECONDS" python "$PLANNER_SCRIPT" "$DOMAIN_PDDL" "$instance_file" -s gbf -H lmcut
            ) || {
                if [ $? -eq 124 ]; then
                    echo "Timeout expired for lmcut on instance $instance_file"
                else
                    echo "Planner exited with an error for lmcut on instance $instance_file"
                fi
            }

            # Check if an lmcut solution file was created and process it
            if [ -f "$output_file" ]; then
                line_count=$(wc -l < "$output_file" | awk '{print $1}')
                echo -e "\t-> lmcut solution found with ${line_count} steps."
                echo "${domain},${instance_basename},${line_count}" >> "$CSV_FILE"
                mv "$output_file" "$DOMAIN_SOLUTION_DIR/"
            else
                echo -e "\t-> No lmcut solution found."
            fi
        fi

        # --- 2. Run the new planner with actionlandmark heuristic ---
        landmark_output_file="${instance_file}.lndmk"
        dest_landmark_file="${DOMAIN_SOLUTION_DIR}/$(basename "$landmark_output_file")"
        
        # Check if landmark solution already exists
        if [ -f "$dest_landmark_file" ] && [ -s "$dest_landmark_file" ]; then
            echo -e "\t-> actionlandmark solution already exists. Skipping."
        else
            (
                ulimit -v "$MEMORY_LIMIT_KB"
                timeout "$TIMEOUT_SECONDS" python "$PLANNER_SCRIPT" "$DOMAIN_PDDL" "$instance_file" -s gbf -H actionlandmark > "$landmark_output_file"
            ) || {
                if [ $? -eq 124 ]; then
                    echo "Timeout expired for actionlandmark on instance $instance_file"
                else
                    echo "Planner exited with an error for actionlandmark on instance $instance_file"
                fi
            }
            
            # Check if the landmark solution file was created (and is not empty)
            if [ -s "$landmark_output_file" ]; then
                echo -e "\t-> actionlandmark solution saved."
                mv "$landmark_output_file" "$DOMAIN_SOLUTION_DIR/"
            else
                echo -e "\t-> No actionlandmark solution found or output was empty."
                # Clean up empty file if it exists
                rm -f "$landmark_output_file"
            fi
        fi

        echo # Add a newline for better readability
    done
done

echo "Benchmark processing complete. Results are in $CSV_FILE"