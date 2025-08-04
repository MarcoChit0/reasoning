#!/bin/bash

path="res/ipc2023-learning/benchmarks"

# Get action landmarks from a task using pyperplan
get_action_landmarks() {
    local domain_path=$1
    local instance_path=$2
    
    # Run pyperplan and capture output
    output=$(pyperplan "$domain_path" "$instance_path" -s astar -H actionlandmark 2>&1)
    
    # Check if pyperplan was successful
    if [ $? -ne 0 ]; then
        echo "Error running pyperplan for $instance_path: $output" >&2
        return 1 # Indicate failure
    fi
    
    # Save output to landmarks file
    echo "$output" > "${instance_path}.landmarks"
    
    # Return list of landmarks (simplified)
    echo "$output"
}

# Iterate over each domain in the specified path
for domain in $(ls "$path"); do
    domain_dir="$path/$domain"
    domain_path="$domain_dir/domain.pddl"

    # Skip if not a directory
    if [ ! -d "$domain_dir" ]; then
        continue
    fi
    
    echo "Processing domain: $domain"
    instance_dir="$domain_dir/testing/easy"

    # Check if 30 landmark files already exist
    if [ $(find "$instance_dir" -name "*.landmarks" | wc -l) -ge 30 ]; then
        echo "Skipping domain $domain: 30 landmark files already exist."
        continue
    fi

    # Initialize counter for instances
    instance_count=0
    
    # Iterate over each instance in the easy testing directory
    for instance in $(ls "$instance_dir"); do
        # Skip files that are not PDDL files
        if [[ ! $instance == *.pddl ]]; then
            continue
        fi
        
        instance_path="$instance_dir/$instance"
        
        # Try to generate action landmarks
        get_action_landmarks "$domain_path" "$instance_path"
        
        # Increment counter regardless of success or failure
        ((instance_count++))
        
        if [ $instance_count -ge 30 ]; then
            echo "Reached 30 instances for domain $domain, moving to next domain."
            break
        fi
    done
done