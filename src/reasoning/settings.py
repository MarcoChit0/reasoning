import os
DATA_DIR = "data/"

# RAW 
RAW_DIR = os.path.join(DATA_DIR, "raw")
STRUCTURE_FILE = os.path.join(RAW_DIR, "structure.yaml")

# EXPERIMENTS
EXPERIMENTS_DIR = os.path.join(DATA_DIR, "experiments")
VALIDATION_FILE_NAME = "validation_results.csv"
METRICS_FILE_NAME = "metrics.csv"