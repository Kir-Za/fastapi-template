# Makefile
.PHONY: help create-venv generate-service clean

PYTHON_VERSION ?= 3.12
VENV_NAME ?= .venv

help: ## Показать это сообщение помощи
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

create-venv: ## Создать виртуальное окружение с uv
	@echo "Создание виртуального окружения Python $(PYTHON_VERSION)..."
	uv venv $(VENV_NAME) --python $(PYTHON_VERSION)
	@echo "Виртуальное окружение создано. Активируйте его: source $(VENV_NAME)/bin/activate"
	uv pip install --upgrade pip jinja2 typer rich

install-deps: ## Установить зависимости генератора
	uv pip install jinja2 typer rich

generate-service: install-deps ## Запустить генератор FastAPI сервиса
	python generator/main.py

clean: ## Очистить сгенерированные файлы и виртуальное окружение
	rm -rf $(VENV_NAME)
	rm -rf generated_service
	@echo "Очистка завершена"
