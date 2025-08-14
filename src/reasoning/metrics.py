import pandas as pd
import os
import numpy as np

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
    group_keys = ['experiment', 'domain', 'model', 'template', 'instance']
    grouped = df.groupby(group_keys)

    df['all_valid'] = df['valid'].astype(int)
    df['any_valid'] = df['valid'].astype(int)
    
    # Assuming 'instance_id' is the column that identifies unique instances
    # If it's a different column, replace 'instance_id' with the correct column name
    agg_funcs = {
        'valid': ['sum', 'count'],
        'all_valid' : lambda x: int(np.all(x)),
        'any_valid' : lambda x: int(np.any(x)),
    }
    results_df = grouped.agg(agg_funcs)

    # Flatten the multi-level column index and rename columns for clarity
    results_df.columns = ['correct_samples', 'total_samples', 'all_valid', 'any_valid']
    results_df = results_df.reset_index()

    # Calculate pass@k for each k up to the maximum number of samples
    max_k = df['sample_id'].max()
    if max_k > 0:
        print(f"Calculating pass@k for k up to {max_k}...")
        for k in range(1, max_k + 1):
            results_df[f'pass@{k}'] = results_df.apply(
                lambda row: pass_at_k(
                    n=row['total_samples'],
                    c=row['correct_samples'],
                    k=k
                ),
                axis=1
            )

    # Group by experiment, domain, model, template to aggregate across instances
    group_cols = ['experiment', 'domain', 'model', 'template']
    agg_dict = {
        'instance': 'count',  # Count of unique instances
        'total_samples': 'sum',
        'correct_samples': 'sum',
        'all_valid': 'mean',
        'any_valid': 'mean'
    }

    # Add pass@k metrics to aggregation dictionary
    for k in range(1, max_k + 1):
        # Fill NaN values with 0 before aggregating
        col_name = f'pass@{k}'
        results_df[col_name] = results_df[col_name].fillna(0)
        agg_dict[col_name] = 'mean'

    # Perform the aggregation
    aggregated_df = results_df.groupby(group_cols).agg(agg_dict)

    # Rename columns for clarity
    aggregated_df.rename(columns={'instance': 'num_instances'}, 
                        inplace=True)

    # Calculate accuracy
    aggregated_df['accuracy_samples'] = aggregated_df['correct_samples'] / aggregated_df['total_samples']
    aggregated_df['accuracy_samples'] = aggregated_df['accuracy_samples'].fillna(0)

    # Reset index to make group columns regular columns again
    aggregated_df = aggregated_df.reset_index()
    
    # Reorder columns to ensure accuracy appears before pass@k metrics
    cols = list(aggregated_df.columns)
    pass_k_cols = [col for col in cols if col.startswith('pass@')]
    other_cols = [col for col in cols if not col.startswith('pass@')]
    new_order = [col for col in other_cols] + pass_k_cols
    aggregated_df = aggregated_df[new_order]
    
    # Round all float columns to two decimal places
    float_cols = aggregated_df.select_dtypes(include=['float']).columns
    aggregated_df[float_cols] = aggregated_df[float_cols].round(2)

    aggregated_df.to_csv(os.path.join(experiment_path, METRICS_FILE_NAME), index=False)

    return aggregated_df


def to_table(df, experiment_path):
    """
    Convert the dataframe resulted from process_data to a "printable table" for easier visualization in LaTeX format.
    The table rows are organized by domain and model, with separate rows for each metric.
    A multi-level header is used to group template columns under a 'templates' label.
    Returns a pandas DataFrame suitable for pretty-printing or LaTeX export.
    """
    # Get unique templates for columns, sort so 'pddl' is first if present
    templates = sorted(df['template'].unique(), key=lambda x: (x != 'pddl', x))
    models = sorted(df['model'].unique())
    domains = sorted(df['domain'].unique())

    # Find all pass@k columns and sort them numerically
    pass_k_cols = sorted([col for col in df.columns if col.startswith('pass@')],
                         key=lambda x: int(x.split('@')[1]))

    # 1. Define all metrics in order, including the new ones
    all_metrics = [
        ('num_instances', 'number_of_instances'),
        ('correct_samples', 'correct_samples'),
        ('total_samples', 'total_samples'),
        ('accuracy_samples', 'Accuracy')
    ]
    all_metrics.extend([(pk, pk) for pk in pass_k_cols])

    # Prepare the table data
    table_data = []
    for domain in domains:
        for model in models:
            metric_rows = [{'domain': domain, 'model': model, 'metric': display_name}
                           for _, display_name in all_metrics]

            for template in templates:
                sub_df = df[(df['domain'] == domain) & 
                            (df['model'] == model) & 
                            (df['template'] == template)]
                
                if not sub_df.empty:
                    record = sub_df.iloc[0]
                    for i, (col_name, _) in enumerate(all_metrics):
                        value = record[col_name]
                        if col_name in ['num_instances', 'correct_samples', 'total_samples']:
                            metric_rows[i][template] = f"{int(value)}"
                        else:
                            metric_rows[i][template] = f"{value:.2f}"
                else:
                    for row in metric_rows:
                        row[template] = ""
            
            table_data.extend(metric_rows)
            # 3. Removed the code that added empty separator rows

    table_df = pd.DataFrame(table_data)
    if table_df.empty:
        print("Warning: No data to create a table.")
        return pd.DataFrame()
        
    table_df = table_df.set_index(['domain', 'model', 'metric'])

    # 2. Add a 'templates' header by creating a MultiIndex for the columns
    if templates:
        table_df.columns = pd.MultiIndex.from_product([['templates'], table_df.columns])

    # 4. Define column format with a vertical line
    column_format = 'lll|' + 'c' * len(templates)

    # Generate LaTeX string with all improvements
    latex_str = table_df.to_latex(
        escape=True,
        column_format=column_format,
        multirow=True,
        multicolumn_format='c'
    )
    
    with open(os.path.join(experiment_path, "table.tex"), "w") as f:
        f.write(latex_str)
    
    return table_df

if __name__ == "__main__":
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
                except Exception as e:
                    print(f"Could not process experiment '{experiment}': {e}")
