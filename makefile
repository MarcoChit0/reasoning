# Makefile for Reasoning Project

# --- Configuration ---
CONDA_ENV_NAME = reasoning
.DEFAULT_GOAL := conda_env

conda_env: environment.yml
	@echo ">>> Creating Conda environment '${CONDA_ENV_NAME}'..."
	@conda env create -f environment.yml