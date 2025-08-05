#!/bin/bash

# This script automates running the Fast Downward planner on a set of benchmarks.
# It iterates through domain and instance files, executes the planner,
# saves the full output to a log file, extracts the plan length,
# and saves the final metrics to a CSV file.

# --- Configuration ---
# Path to the Fast Downward executable
FAST_DOWNWARD_EXEC="../downward/fast-downward.py"
# Directory containing the benchmark domains
BENCHMARKS_DIR="./data/benchmarks"
# The output CSV file where metrics will be stored
OUTPUT_CSV="downward_metrics.csv"
# The root directory to store raw output logs from the planner
LOGS_DIR="fast-downward"
# The search algorithm to be used by Fast Downward
SEARCH_ALGORITHM="astar(ff())"

# --- Initialization ---
# Create the output file and write the CSV header.
# This will overwrite the file if it already exists.
echo "domain,instance,steps" > "$OUTPUT_CSV"
# Create the main logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"
echo "Starting benchmark run..."

# --- Main Loop ---
# Find all domain directories within the benchmarks directory.
for domain_path in "$BENCHMARKS_DIR"/*/; do
    # Check if it's a directory
    if [ ! -d "$domain_path" ]; then
        continue
    fi

    # Extract the domain name from its path
    domain=$(basename "$domain_path")
    echo "Processing domain: $domain"

    # --- ADDED FEATURE: Create domain-specific log directory ---
    domain_log_dir="$LOGS_DIR/$domain"
    mkdir -p "$domain_log_dir"

    # Define the path to the domain's PDDL file
    pddl_domain_path="${domain_path}domain.pddl"

    # Check if the domain PDDL file exists
    if [ ! -f "$pddl_domain_path" ]; then
        echo "  WARNING: Domain file not found at $pddl_domain_path. Skipping."
        continue
    fi

    # Define the path to the instances directory
    instances_dir="${domain_path}instances"

    # Check if the instances directory exists
    if [ ! -d "$instances_dir" ]; then
        echo "  WARNING: Instances directory not found at $instances_dir. Skipping domain."
        continue
    fi

    # Find all PDDL instance files recursively within the instances directory
    find "$instances_dir" -type f -name "*.pddl" | while read -r instance_path; do
        # Extract the instance filename from its path
        instance=$(basename "$instance_path")
        echo "  Running instance: $instance"

        # --- ADDED FEATURE: Define the output log file path ---
        # It removes the '.pddl' extension and adds '.txt'
        instance_log_file="$domain_log_dir/${instance%.pddl}.txt"

        # Construct the command to execute
        command=("$FAST_DOWNWARD_EXEC" "$pddl_domain_path" "$instance_path" --search "$SEARCH_ALGORITHM")

        # --- MODIFIED EXECUTION: Save output to log file ---
        # Execute the command, redirecting stdout to the log file and stderr to /dev/null
        "${command[@]}" > "$instance_log_file" 2>/dev/null

        # --- MODIFIED EXTRACTION: Read from the log file ---
        # Use grep to find the plan length directly from the newly created log file.
        plan_length=$(grep -oP 'Plan length: \K[0-9]+' "$instance_log_file")

        # Check if a plan length was successfully extracted
        if [[ -n "$plan_length" && "$plan_length" =~ ^[0-9]+$ ]]; then
            echo "    -> Found Plan Length: $plan_length. Log saved to $instance_log_file"
            # Append the results to the CSV file
            echo "$domain,$instance,$plan_length" >> "$OUTPUT_CSV"
        else
            echo "    -> Plan not found or error. Log saved to $instance_log_file"
        fi
    done
done

echo "Benchmark run finished. Results saved to $OUTPUT_CSV and logs to $LOGS_DIR/"
