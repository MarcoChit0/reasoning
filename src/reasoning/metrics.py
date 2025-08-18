import pandas as pd
import os
import numpy as np

# --- Constants (placeholders for your settings) ---
from reasoning.settings import EXPERIMENTS_DIR, VALIDATION_FILE_NAME, PASS_AT_K_METRIC_FILE_NAME


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

def compute_pass_at_k(experiment_path):
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
    
    # Assuming 'instance_id' is the column that identifies unique instances
    # If it's a different column, replace 'instance_id' with the correct column name
    agg_funcs = {
        'valid': ['sum', 'count'],
        'num_action_landmarks': 'mean',
        'num_action_landmarks_used': 'mean'
    }
    results_df = grouped.agg(agg_funcs)

    # Flatten the multi-level column index and rename columns for clarity
    results_df.columns = ['correct_samples', 'total_samples', 'num_action_landmarks', 'num_action_landmarks_used']
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
        'num_action_landmarks': 'mean',
        'num_action_landmarks_used': 'mean'
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

    aggregated_df.to_csv(os.path.join(experiment_path, PASS_AT_K_METRIC_FILE_NAME), index=False)

    return aggregated_df


def pass_at_k_to_table(df, experiment_path):
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

    # Define all metrics in the desired order for the table rows.
    all_metrics = [
        ('num_instances', 'number_of_instances'),
        ('correct_samples', 'correct_samples'),
        ('total_samples', 'total_samples'),
        ('num_action_landmarks_used', 'number_of_used_landmarks'),
        ('num_action_landmarks', 'number_of_landmarks'),
        ('accuracy_samples', 'Accuracy')
    ]
    # --- MODIFICATION 1: Manually replace '@' for LaTeX compatibility ---
    # Use a display name that is safe for LaTeX, e.g., 'pass-at-k'
    all_metrics.extend([(pk, pk.replace('@', '-at-')) for pk in pass_k_cols])

    # Prepare the table data
    table_data = []
    for domain in domains:
        for model in models:
            # Initialize a dictionary for each metric row
            metric_rows = [{'domain': domain, 'model': model, 'metric': display_name}
                           for _, display_name in all_metrics]

            for template in templates:
                sub_df = df[(df['domain'] == domain) & 
                            (df['model'] == model) & 
                            (df['template'] == template)]
                
                if not sub_df.empty:
                    record = sub_df.iloc[0]
                    for i, (col_name, _) in enumerate(all_metrics):
                        value = record.get(col_name) # Use .get() for safety
                        if value is None:
                             metric_rows[i][template] = ""
                        # Format integers without decimal points
                        elif col_name in ['num_instances', 'correct_samples', 'total_samples']:
                            metric_rows[i][template] = f"{int(value)}"
                        else:
                            metric_rows[i][template] = f"{value:.2f}"
                else:
                    for row in metric_rows:
                        row[template] = ""
            
            table_data.extend(metric_rows)

    table_df = pd.DataFrame(table_data)
    if table_df.empty:
        print("Warning: No data to create a table.")
        return

    table_df = table_df.set_index(['domain', 'model', 'metric'])

    # Add a 'templates' header by creating a MultiIndex for the columns
    if templates:
        table_df.columns = pd.MultiIndex.from_product([['templates'], table_df.columns])

    # Define column format with a vertical line
    column_format = 'lll|' + 'c' * len(templates)

    # --- MODIFICATION 2: Change escape back to True ---
    # This correctly handles underscores and other special characters automatically.
    latex_table_content = table_df.to_latex(
        escape=True,
        column_format=column_format,
        multirow=True,
        multicolumn_format='c'
    )
    
    # Add a reminder about the required LaTeX package
    latex_header = "% In your LaTeX preamble, make sure you have: \\usepackage{graphicx}\n"
    # Wrap the table in a scalebox to control its width. Adjust the scale (e.g., 0.6) as needed.
    latex_str = f"{latex_header}\\scalebox{{0.6}}{{\n{latex_table_content}}}"

    with open(os.path.join(experiment_path, PASS_AT_K_METRIC_FILE_NAME.replace(".csv", ".table.tex")), "w") as f:
        f.write(latex_str)

def compute_metrics_by_attempt(experiment_path : str) -> pd.DataFrame:
    if not os.path.exists(experiment_path):
        raise FileNotFoundError(f"Experiment path {experiment_path} does not exist.")

    validation_path = os.path.join(experiment_path, VALIDATION_FILE_NAME)
    if not os.path.exists(validation_path):
        raise FileNotFoundError(f"Validation file {validation_path} does not exist.")
    
    df = pd.read_csv(validation_path)
    # Ensure 'valid' column is boolean
    df['valid'] = pd.to_numeric(df['valid'], errors='coerce').fillna(0).astype(bool)
    instances = df['instance'].unique()

    # Group by the specified columns to aggregate results
    group_keys = ['experiment', 'domain', 'model', 'template']
    grouped = df.groupby(group_keys)

    new_df = pd.DataFrame()
    for (name, group) in grouped:
        max_sample_id = group['sample_id'].max()
        for instance in instances:
            instance_group = group[group['instance'] == instance]
            if instance_group.empty:
                continue
            samples_metrics = {
                "num_action_landmarks_used_at" : [0 for _ in range(max_sample_id)],
                "valid_at" : [False for _ in range(max_sample_id)],
            }
            for i in range(1, max_sample_id + 1):
                sample_group = instance_group[instance_group['sample_id'] == i]
                if sample_group.empty:
                    continue
                sample_df = sample_group.iloc[0]
                num_action_landmarks = sample_df['num_action_landmarks']
                for j in range(i-1, max_sample_id):
                    samples_metrics["num_action_landmarks_used_at"][j] += sample_df['num_action_landmarks_used']
                    samples_metrics["valid_at"][j] |= sample_df['valid']

                samples_metrics["num_action_landmarks_used_at"][i-1] /= i

                new_df = new_df._append({
                    "experiment": name[0],
                    "domain": name[1],
                    "model": name[2],
                    "template": name[3],
                    "instance": instance,
                    "num_action_landmarks_used_at": samples_metrics["num_action_landmarks_used_at"][i-1],
                    "valid_at": samples_metrics["valid_at"][i-1],
                    "attempts": i,
                    "num_action_landmarks": num_action_landmarks
                }, ignore_index=True)
    
    new_df = new_df.groupby(['experiment', 'domain', 'model', 'template', 'attempts']).agg({
        "instance": "count",
        "num_action_landmarks_used_at": "mean",
        "valid_at": "mean",
        "num_action_landmarks": "mean"
    }).reset_index()
    
    # Round all float columns to two decimal places
    float_cols = new_df.select_dtypes(include=['float']).columns
    new_df[float_cols] = new_df[float_cols].round(2)

    new_df.to_csv(os.path.join(experiment_path, "metrics_by_attempt.csv"), index=False)

    return new_df

def metrics_by_attempt_to_table(df: pd.DataFrame, experiment_path: str):
    """
    Converts the DataFrame from compute_metrics_by_attempt into a LaTeX table.

    The table is structured similarly to the provided example, with multi-level
    row indexing for domain, model, metric, and attempt. It generates a .tex file
    with the formatted table.
    """
    if df.empty:
        print("Warning: DataFrame is empty. Cannot generate metrics by attempt table.")
        return

    # 1. Prepare data by pivoting
    # Rename columns for clarity and prepare for pivoting
    df = df.rename(columns={
        'num_action_landmarks_used_at': 'used_landmarks',
        'attempts': 'attempt'
    })

    # Melt the DataFrame to handle multiple metric columns easily
    metrics_to_display = ['used_landmarks', 'valid_at']
    melted_df = df.melt(
        id_vars=['domain', 'model', 'template', 'attempt'],
        value_vars=metrics_to_display,
        var_name='metric',
        value_name='value'
    )
    
    # Escape underscores in metric names for LaTeX
    melted_df['metric'] = melted_df['metric'].str.replace('_', r'\_')
    
    # Get unique, sorted lists for columns and metric order
    templates = sorted(df['template'].unique())
    metrics_order = [m.replace('_', r'\_') for m in metrics_to_display]

    # Pivot to the final table structure
    table_df = melted_df.pivot_table(
        index=['domain', 'model', 'metric', 'attempt'],
        columns='template',
        values='value'
    )
    
    # Ensure the order of templates (columns) and metrics (index level) is correct
    table_df = table_df.reindex(templates, axis='columns')
    table_df = table_df.reindex(metrics_order, level='metric')


    # 2. Build the LaTeX string manually for full control
    num_templates = len(templates)
    column_format = 'llll|' + 'c' * num_templates

    # Header
    escaped_templates = [t.replace('_', r'\_') for t in templates]
    template_header = ' & '.join(escaped_templates)
    
    latex_lines = [
        f"\\begin{{tabular}}{{{column_format}}}",
        "\\toprule",
        # Multi-column header for 'templates'
        f" & & & & \\multicolumn{{{num_templates}}}{{c}}{{templates}} \\\\",
        f"domain & model & metric & attempt & {template_header} \\\\",
        "\\midrule"
    ]

    # 3. Generate table body with multirow and clines
    # Group by the first two index levels (domain, model)
    for (domain, model), group in table_df.groupby(level=['domain', 'model']):
        domain_model_group_size = len(group)
        domain_multirow = f"\\multirow[t]{{{domain_model_group_size}}}{{*}}{{{domain}}}"
        model_multirow = f"\\multirow[t]{{{domain_model_group_size}}}{{*}}{{{model}}}"
        
        is_first_row_in_domain_group = True
        
        # Group by the metric within the current domain/model block
        for metric, metric_group in group.groupby(level='metric'):
            metric_group_size = len(metric_group)
            metric_multirow = f"\\multirow[t]{{{metric_group_size}}}{{*}}{{{metric}}}"
            
            is_first_row_in_metric_group = True

            # Iterate through each attempt in the metric group to create the rows
            for (_, _, _, attempt), row_data in metric_group.iterrows():
                values = [f"{v:.2f}" if pd.notna(v) else "" for v in row_data]
                values_str = ' & '.join(values)

                # Add domain/model only for the first row of the block
                line = f"{domain_multirow} & {model_multirow}" if is_first_row_in_domain_group else " & "
                is_first_row_in_domain_group = False
                
                # Add metric name only for the first row of its sub-block
                if is_first_row_in_metric_group:
                    line += f" & {metric_multirow} & {attempt} & {values_str} \\\\"
                    is_first_row_in_metric_group = False
                else:
                    line += f" & & {attempt} & {values_str} \\\\"
                
                latex_lines.append(line)

            # Add a \cline after a metric block, if it's not the last one in the domain/model group
            metrics_in_group = group.index.get_level_values('metric').unique()
            if metric != metrics_in_group[-1]:
                cline_start_col = 3  # Start at the 'metric' column
                cline_end_col = 4 + num_templates # End at the last template column
                latex_lines.append(f"\\cline{{{cline_start_col}-{cline_end_col}}}")

        latex_lines.append("\\midrule")
    
    # Clean up the last separator before the bottom rule
    if latex_lines[-1] == "\\midrule":
        latex_lines.pop()
        
    # Footer
    latex_lines.append("\\bottomrule")
    latex_lines.append("\\end{tabular}")
    
    # 4. Finalize and save the file
    full_latex_string = '\n'.join(latex_lines)
    
    # Wrap in scalebox for better fitting on a page
    final_output = (
        "% In your LaTeX preamble, make sure you have: \\usepackage{graphicx}, \\usepackage{multirow}, \\usepackage{booktabs}\n"
        "\\scalebox{0.6}{\n"
        f"{full_latex_string}\n"
        "}"
    )

    output_filename = os.path.join(experiment_path, "metrics_by_attempt.table.tex")
    with open(output_filename, "w") as f:
        f.write(final_output)

    print(f"LaTeX table of metrics by attempt saved to {output_filename}")

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
                    pass_at_k_to_table(compute_pass_at_k(experiment_path), experiment_path)
                    metrics_by_attempt_to_table(compute_metrics_by_attempt(experiment_path), experiment_path)
                    
                except Exception as e:
                    print(f"Could not process experiment '{experiment}': {e}")
