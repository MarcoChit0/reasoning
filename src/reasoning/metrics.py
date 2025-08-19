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

    df['landmarks'] = df['num_action_landmarks_used'] / df['num_action_landmarks'].replace(0, np.nan)
    # Group by the specified columns to aggregate results
    group_keys = ['experiment', 'domain', 'model', 'template', 'sample_id']
    grouped = df.groupby(group_keys).agg({
        "instance": "count",
        "valid": "mean",
        "landmarks": "mean"
    }).reset_index()

    # rename:
    # sample_id -> attempt
    # instance -> total_instances
    # valid -> coverage
    grouped = grouped.rename(columns={"sample_id": "attempt", "instance": "total_instances", "valid": "coverage"})

    # Round all float columns to two decimal places
    float_cols = grouped.select_dtypes(include=['float']).columns
    grouped[float_cols] = grouped[float_cols].round(2)

    grouped.to_csv(os.path.join(experiment_path, "metrics_by_attempt.csv"), index=False)

    return grouped

def metrics_by_attempt_to_table(df: pd.DataFrame, experiment_path: str):
    """
    Generates a LaTeX table where each row corresponds to an attempt, and columns
    are grouped by template, each showing 'Coverage' and 'Landmarks' metrics.
    """
    if df.empty:
        print("Warning: DataFrame is empty. Cannot generate metrics by attempt table.")
        return

    # --- 1. Reshape the DataFrame for the new table structure ---
    metrics_to_display = ['coverage', 'landmarks']
    
    table_df = df.pivot_table(
        index=['domain', 'model', 'attempt'],
        columns='template',
        values=metrics_to_display
    )

    table_df = table_df.swaplevel(0, 1, axis=1)

    # --- 2. Define the exact column order and names (MODIFIED SECTION) ---
    
    # Get all unique template names from the original DataFrame
    all_templates = df['template'].unique()
    
    # Define the custom sort order
    # 'pddl' comes first, the rest are sorted alphabetically
    # We use a lambda function where 'pddl' is given a special low sort key (False)
    templates = sorted(all_templates, key=lambda x: (x != 'pddl', x))
    
    # Create an explicit list of column tuples to enforce the desired order.
    new_cols_tuples = []
    for template in templates:
        for metric in metrics_to_display: 
            new_cols_tuples.append((template, metric))
    
    new_cols = pd.MultiIndex.from_tuples(new_cols_tuples, names=['template', 'metric'])
    table_df = table_df.reindex(columns=new_cols)

    # --- 3. Build the LaTeX string manually for full control ---
    num_templates = len(templates)
    column_format = 'lll|' + 'cc' * num_templates

    # Define the new display names for the templates (MODIFIED SECTION)
    template_name_map = {
        'pddl': '-',
        'random_new_landmark': 'Non-Ordered Landmarks',
        'delete_relaxed_plan': 'Delete Relaxation',
        'ordered_landmark_explicit': 'Ordered Landmarks',
        'ordered_landmark_omitted': 'Ordered Landmarks (Omitted)'
    }
    
    # --- LaTeX Header Generation ---
    template_headers = [template_name_map.get(t, t.replace('_', ' ').title()) for t in templates]
    template_header_str = ' & '.join([f"\\multicolumn{{2}}{{c}}{{{name}}}" for name in template_headers])
    
    metric_header_str = ' & '.join(["Coverage & Landmarks"] * num_templates)

    latex_lines = [
        f"\\begin{{tabular}}{{{column_format}}}",
        "\\toprule",
        # First header row (templates)
        f"domain & model & attempt & {template_header_str} \\\\",
        # Use \cmidrule for a clean line under the template headers
        f"\\cmidrule(lr){{4-{3 + 2 * num_templates}}}",
        # Second header row (metrics)
        f"& & & {metric_header_str} \\\\",
        "\\midrule"
    ]

    # --- LaTeX Body Generation (No changes here) ---
    for (domain, model), group in table_df.groupby(level=['domain', 'model']):
        group_size = len(group)
        domain_multirow = f"\\multirow[t]{{{group_size}}}{{*}}{{{domain}}}"
        model_multirow = f"\\multirow[t]{{{group_size}}}{{*}}{{{model}}}"
        is_first_row_in_group = True

        for (_, _, attempt), row_data in group.iterrows():
            values_str = ' & '.join([f"{v:.2f}" if pd.notna(v) else "" for v in row_data])

            if is_first_row_in_group:
                line = f"{domain_multirow} & {model_multirow} & {attempt} & {values_str} \\\\"
                is_first_row_in_group = False
            else:
                line = f" & & {attempt} & {values_str} \\\\"
            
            latex_lines.append(line)
        
        latex_lines.append("\\midrule")

    if latex_lines[-1] == "\\midrule":
        latex_lines.pop()
        
    latex_lines.extend(["\\bottomrule", "\\end{tabular}"])

    # --- 4. Finalize and Save (No changes here) ---
    full_latex_string = '\n'.join(latex_lines)
    final_output = (
        "% In your LaTeX preamble, use: \\usepackage{graphicx}, \\usepackage{multirow}, \\usepackage{booktabs}\n"
        "\\begin{table}[H] % Using [H] from 'float' package to place table here\n"
        "\\centering\n"
        "\\scalebox{0.7}{\n"
        f"{full_latex_string}\n"
        "}\n"
        "\\caption{Metrics by Attempt}\n"
        "\\label{tab:metrics_by_attempt}\n"
        "\\end{table}"
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
