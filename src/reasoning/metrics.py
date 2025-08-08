import pandas as pd
import os
import numpy as np
import re

# --- Constants (placeholders for your settings) ---
from reasoning.settings import EXPERIMENTS_DIR, VALIDATION_FILE_NAME, METRICS_FILE_NAME


def pass_at_k(n, c, k):
    """
    Calculates the pass@k metric.
    :param n: total number of samples.
    :param c: number of correct samples.
    :param k: the 'k' in pass@k.
    """
    if n < k or n == 0:
        return np.nan
    # This is an unbiased estimator for pass@k.
    # It calculates 1 - (C(n-c, k) / C(n, k))
    if k > n - c:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))

def process_data(experiment_path):
    """
    Reads validation data for a single experiment, calculates metrics,
    and returns a processed DataFrame.
    """
    if not os.path.exists(experiment_path):
        raise FileNotFoundError(f"Experiment path {experiment_path} does not exist.")

    validation_path = os.path.join(experiment_path, VALIDATION_FILE_NAME)
    if not os.path.exists(validation_path):
        raise FileNotFoundError(f"Validation file {validation_path} does not exist.")
    
    df = pd.read_csv(validation_path)
    # Ensure 'valid' column is boolean
    df['valid'] = pd.to_numeric(df['valid'], errors='coerce').fillna(0).astype(bool)

    # Group by the specified columns to aggregate results
    group_keys = ['experiment', 'domain', 'instance_subdir', 'model', 'template']
    grouped = df.groupby(group_keys)
    
    agg_funcs = {
        'sample_id': 'max',
        'valid': ['sum', 'count'],
        'candidates_token_count': 'mean',
        'num_action_landmarks': 'mean',
    }
    results_df = grouped.agg(agg_funcs)

    # Flatten the multi-level column index and rename columns for clarity
    results_df.columns = ['max_samples', 'correct_instances', 'total_instances', 'candidates_token_count', 'num_action_landmarks']
    results_df = results_df.reset_index()

    # Calculate accuracy, handling division by zero
    results_df['accuracy'] = results_df['correct_instances'] / results_df['total_instances']
    results_df['accuracy'] = results_df['accuracy'].fillna(0)

    # Calculate pass@k for each k up to the maximum number of samples
    max_k = df['sample_id'].max()
    if max_k > 0:
        print(f"Calculating pass@k for k up to {max_k}...")
        for k in range(1, max_k + 1):
            results_df[f'pass@{k}'] = results_df.apply(
                lambda row: pass_at_k(
                    n=row['total_instances'],
                    c=row['correct_instances'],
                    k=k
                ),
                axis=1
            )

    # Save the metrics for this specific experiment
    metrics_path = os.path.join(experiment_path, METRICS_FILE_NAME)
    results_df.to_csv(metrics_path, index=False)

    return results_df

def get_instance_sort_key(subdir_string):
    """
    Creates a sort key for the 'instance_subdir' column.
    It extracts the numeric prefix from the last component of the path.
    If the format is not '<number>-<string>', it prepares for alphabetical sorting.
    """
    # Handle empty or non-string values gracefully
    if not isinstance(subdir_string, str) or not subdir_string:
        # Sort these values after the formatted ones
        return (1, subdir_string) 

    try:
        # Get the last part of the path (e.g., '4-blocks' from 'sub/dir/4-blocks')
        last_component = subdir_string.split('/')[-1]
        # Use regex to find a number at the start of the string
        match = re.match(r'^\d+', last_component)
        if match:
            # If a number is found, use it for sorting. The '0' ensures these come first.
            return (0, int(match.group(0)))
        else:
            # If no number is found, fall back to alphabetical sorting
            return (1, subdir_string)
    except (ValueError, IndexError):
        # Fallback for any other malformed strings
        return (1, subdir_string)

def to_table(df, experiment_path):
    """
    Convert the dataframe resulted from process_data to a "printable table" for easier visualization in LaTeX format.
    The table rows are (domain, model), columns are templates, and each cell contains '#correct / #instances'.
    Returns a pandas DataFrame suitable for pretty-printing or LaTeX export.
    """
    # Get unique templates for columns, sort so 'pddl' is first if present
    templates = sorted(df['template'].unique(), key=lambda x: (x != 'pddl', x))
    # Get unique models and domains for rows
    models = sorted(df['model'].unique())
    domains = sorted(df['domain'].unique())

    # Prepare the table data
    table_data = []
    for domain in domains:
        for model in models:
            row = {'domain': domain, 'model': model}
            for template in templates:
                sub_df = df[(df['domain'] == domain) & (df['model'] == model) & (df['template'] == template)]
                if not sub_df.empty:
                    correct = int(sub_df['correct_instances'].sum()) if 'correct_instances' in sub_df else 0
                    total = int(sub_df['total_instances'].sum()) if 'total_instances' in sub_df else 0
                    row[template] = f"{correct} / {total}"
                else:
                    row[template] = ""
            table_data.append(row)

    # Create the final DataFrame
    table_df = pd.DataFrame(table_data)
    # Set 'domain' and 'model' as index for pretty printing
    table_df = table_df.set_index(['domain', 'model'])

    # Save as LaTeX file, remove the last two lines (bottom rule and empty line)
    latex_str = table_df.to_latex(escape=True, column_format='ll' + 'l' * len(templates))
    latex_lines = latex_str.strip().split('\n')
    # Remove the second-to-last line (bottom rule) and last line (end tabular)
    if len(latex_lines) > 2:
        latex_str = '\n'.join(latex_lines[:-2] + [latex_lines[-1]])
    with open(os.path.join(experiment_path, "table.tex"), "w") as f:
        f.write(latex_str)


if __name__ == "__main__":
    # --- 1. Load and process data from all experiments ---
    all_results_df = pd.DataFrame()
    
    # Check if the main experiments directory exists before proceeding
    if not os.path.isdir(EXPERIMENTS_DIR):
        print(f"Error: Experiments directory not found at '{EXPERIMENTS_DIR}'")
    else:
        for experiment in sorted(os.listdir(EXPERIMENTS_DIR)): # Sort for consistent processing order
            experiment_path = os.path.join(EXPERIMENTS_DIR, experiment)
            if os.path.isdir(experiment_path):
                try:
                    print(f"Processing experiment: {experiment}...")
                    result_df = process_data(experiment_path)
                    to_table(result_df, experiment_path)
                    all_results_df = pd.concat([all_results_df, result_df], ignore_index=True)
                except Exception as e:
                    print(f"Could not process experiment '{experiment}': {e}")

    # --- 2. Perform Sorting if any data was successfully loaded ---
    if not all_results_df.empty:
        print("\nAll experiments processed. Now sorting combined data...")
        
        # Create a temporary column with a sortable key for 'instance_subdir'
        all_results_df['instance_sort_key'] = all_results_df['instance_subdir'].apply(get_instance_sort_key)
        
        # Define the sorting hierarchy and order
        sort_by_columns = ['domain', 'instance_sort_key', 'model', 'template']
        ascending_order = [True,       True,                True,      False]

        # Apply the sorting
        sorted_df = all_results_df.sort_values(
            by=sort_by_columns,
            ascending=ascending_order
        )
        
        # --- 3. Finalize and Display ---
        # Drop the temporary sort key column as it's no longer needed
        # Also drop 'experiment' if you want to see a unified table across all experiments
        final_df = sorted_df.drop(columns=['instance_sort_key'])

        # Save the final sorted and combined metrics file to the main experiments directory
        final_metrics_path = os.path.join(EXPERIMENTS_DIR, METRICS_FILE_NAME)
        print(f"Saving combined and sorted metrics to {final_metrics_path}")
        final_df.to_csv(final_metrics_path, index=False)

        # Display the final, sorted results in the console
        print("\n--- Sorted Results ---")
        print(final_df.to_string(index=False))
    else:
        print("\nNo data was processed. Exiting.")
