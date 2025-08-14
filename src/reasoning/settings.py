import os
DATA_DIR = "data/"

# BENCHMARKS
BENCHMARKS_DIR = os.path.join(DATA_DIR, "benchmarks")

# EXPERIMENTS
EXPERIMENTS_DIR = os.path.join(DATA_DIR, "experiments")
VALIDATION_FILE_NAME = "validation_results.csv"
METRICS_FILE_NAME = "metrics.csv"
ERROR_TYPES_FILE_NAME = "error_types.csv"
PROMPT_FILE_NAME = "prompt.log"
SAMPLE_FILE_NAME = "sample_{}.log"
VALIDATED_LOG_FILE_FILE_NAME = "sample_{}.val"

# SOLUTIONS
SOLUTIONS_DIR = os.path.join(DATA_DIR, "solutions")