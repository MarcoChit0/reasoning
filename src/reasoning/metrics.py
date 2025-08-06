import pandas as pd
import os
import numpy as np
from reasoning.settings import VALIDATION_FILE_NAME, EXPERIMENTS_DIR, METRICS_FILE_NAME

def pass_at_k(n, c, k):
    if k > n:
        return np.nan
    # compute 1 - comb(n - c, k) / comb(n, k)
    if k > n - c:
        return 1.0
    return 1 - np.prod(1 - k / np.arange(n - c + 1, n + 1))

def process_data(experiment_path):
    if not os.path.exists(experiment_path):
        raise FileNotFoundError(f"Experiment path {experiment_path} does not exist.")

    validation_path = os.path.join(experiment_path, VALIDATION_FILE_NAME)
    if not os.path.exists(validation_path):
        raise FileNotFoundError(f"Validation file {validation_path} does not exist.")
    
    df = pd.read_csv(validation_path)
    df['valid'] = pd.to_numeric(df['valid'], errors='coerce').fillna(0).astype(bool)

    grouped = df.groupby(['experiment', 'domain', 'instance_subdir', 'model', 'template'])
    agg_funcs = {
        'sample_id': 'max',
        'valid': ['sum', 'count'],
        'candidates_token_count': 'mean',
        'num_action_landmarks': 'mean',
    }
    results_df = grouped.agg(agg_funcs)

    results_df.columns = ['max_samples', 'correct_instances', 'total_instances', 'candidates_token_count', 'num_action_landmarks']
    results_df = results_df.reset_index()

    results_df['accuracy'] = results_df['correct_instances'] / results_df['total_instances']
    results_df['accuracy'] = results_df['accuracy'].fillna(0)

    max_k = df['sample_id'].max()
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

    metrics_path = os.path.join(experiment_path, METRICS_FILE_NAME)
    results_df.to_csv(metrics_path, index=False)

    return results_df

if __name__ == "__main__":
    df = pd.DataFrame()
    for experiment in os.listdir(EXPERIMENTS_DIR):
        experiment_path = os.path.join(EXPERIMENTS_DIR, experiment)
        if os.path.isdir(experiment_path):
            try:
                result_df = process_data(experiment_path)
                df = pd.concat([df, result_df], ignore_index=True)
            except Exception as e:
                print(f"Error processing experiment {experiment}: {e}")
    
    metrics_path = os.path.join(EXPERIMENTS_DIR, METRICS_FILE_NAME)
    df.to_csv(metrics_path, index=False)
    def key_instance_subdir(s):
        try:
            instance = s.split('/')[-1]
            n = instance.split('-')[0]
            return int(n)
        except:
            return s
    grouped_df = df.groupby(['experiment', 'domain', 'instance_subdir', 'model', 'template']).mean().reset_index()
    # Create a temporary column for sorting instance_subdir
    grouped_df['instance_sort_key'] = grouped_df['instance_subdir'].apply(key_instance_subdir)
    # Sort by experiment and domain first, then by the numeric instance value, and template in descending order
    sorted_df = grouped_df.sort_values(
        by=['experiment', 'domain', 'instance_sort_key', 'template'],
        ascending=[True, True, True, False]
    )
    # Drop the temporary column before printing
    sorted_df = sorted_df.drop(['instance_sort_key', 'experiment'], axis=1)
    print(sorted_df.to_string(index=False))