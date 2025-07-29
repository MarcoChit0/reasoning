# Makefile for Reasoning Project

# --- Configuration ---
CONDA_ENV_NAME = reasoning
.DEFAULT_GOAL := conda_env

conda_env: environment.yml
	@echo ">>> Creating Conda environment '${CONDA_ENV_NAME}'..."
	@conda env create -f environment.yml

build_val:
	@echo ">>> Building VAL..."
	@cd res/val && \
	rm -rf build && \
	mkdir build && \
	cd build && \
	cmake .. -DCMAKE_POLICY_VERSION_MINIMUM=3.5 && \
	make && \
	cd ../../..

build_pyperplan:
	@echo ">>> Building Pyperplan..."
	@cd res/pyperplan && \
	pip install -e . && \
	cd ../..

build_submodules:
	@echo ">>> Initializing git submodules..."
	@git submodule init
	@git submodule update
	@$(MAKE) build_val
	@$(MAKE) build_pyperplan
