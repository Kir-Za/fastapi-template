# Makefile
.PHONY: help create-venv generate-service clean

PYTHON_VERSION ?= 3.12
VENV_NAME ?= .venv

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

create-venv: ## Create a virtual environment with uv
	@echo "Creating a Python virtual environment $(PYTHON_VERSION)..."
	uv venv $(VENV_NAME) --python $(PYTHON_VERSION)
	@echo "The virtual environment has been created. Activate it: source $(VENV_NAME)/bin/activate"
	uv pip install --upgrade pip jinja2 typer rich

install-deps: ## Install the generator dependencies
	uv pip install jinja2 typer rich

generate-service: install-deps ## Start the FastAPI service generator
	python generator/main.py

clean: ## Clear the generated files and the virtual environment
	rm -rf $(VENV_NAME)
	rm -rf generated_service
	@echo "Cleaning is complete"
