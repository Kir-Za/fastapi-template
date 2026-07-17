#!/usr/bin/env python3
"""
FastAPI Service Generator
"""

import sys
from pathlib import Path
from typing import Dict, Any

import typer
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

app = typer.Typer()
console = Console()

class FastAPIGenerator:
    def __init__(self):
        self.templates_dir = Path(__file__).parent / "templates"
        console.print(f"[dim]Templates directory: {self.templates_dir}[/dim]")
        
        if not self.templates_dir.exists():
            console.print(f"[red]Error: Templates directory not found: {self.templates_dir}[/red]")
            sys.exit(1)
            
        self.env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
        self.env.trim_blocks = True
        self.env.lstrip_blocks = True
        
    def get_service_config(self) -> Dict[str, Any]:
        """Getting the service configuration through an interactive dialog"""
        console.print(Panel.fit(
            "[bold cyan]🚀 FastAPI Service Generator[/bold cyan]\n"
            "[dim]Creating a microservice[/dim]\n"
            "[dim]Support: Redis, RabbitMQ, LangChain, LangFuse[/dim]"
        ))
        
        config = {
            "service_name": Prompt.ask(
                "Enter the name of the service",
                default="fastapi-service"
            ),
            "python_version": Prompt.ask(
                "Python version",
                default="3.12"
            ),
            "port": Prompt.ask(
                "The port for the service",
                default="8000"
            ),
            "features": {}
        }
        
        console.print("\n[bold]Select the components for the service:[/bold]")
        
        config["features"]["redis"] = Confirm.ask(
            "📦 Connect Redis?",
            default=True
        )
        
        config["features"]["rabbitmq"] = Confirm.ask(
            "🐰 Connect RabbitMQ?",
            default=False
        )
        
        if config["features"]["rabbitmq"]:
            config["rabbitmq_vhost"] = Prompt.ask(
                "RabbitMQ Virtual Host",
                default="/"
            )
        
        config["features"]["langchain"] = Confirm.ask(
            "🔗 Connect LangChain?",
            default=True
        )
        
        config["features"]["langfuse"] = Confirm.ask(
            "📊 Connect LangFuse (observability)?",
            default=True
        )
        
        if config["features"]["langfuse"]:
            config["langfuse_public_key"] = Prompt.ask(
                "LangFuse Public Key",
                default="pk-lf-..."
            )
            config["langfuse_secret_key"] = Prompt.ask(
                "LangFuse Secret Key",
                default="sk-lf-..."
            )
            config["langfuse_host"] = Prompt.ask(
                "LangFuse Host",
                default="https://cloud.langfuse.com"
            )
        
        return config
    
    def render_template(self, template_path: str, config: Dict[str, Any]) -> str:
        try:
            template = self.env.get_template(template_path)
            return template.render(**config)
        except TemplateNotFound:
            console.print(f"[red]Template not found: {template_path}[/red]")
            raise
    
    def generate(self, config: Dict[str, Any], output_dir: str = "generated_service"):
        output_path = Path(output_dir)
        
        console.print(f"\n[bold green]Service generation '{config['service_name']}'...[/bold green]")
        
        directories = [
            output_path,
            output_path / "src",
            output_path / "src" / "api",
            output_path / "src" / "connections",
            output_path / "src" / "langchain",
            output_path / "tests",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            console.print(f"  [dim]Created directory: {directory}[/dim]")
        

        templates = {
            "Dockerfile.j2": "Dockerfile",
            "docker-compose.yml.j2": "docker-compose.yml",
            ".env.example.j2": ".env.example",
            ".dockerignore.j2": ".dockerignore",
            ".gitignore.j2": ".gitignore",
            "README.md.j2": "README.md",
            "src/__init__.py.j2": "src/__init__.py",
            "src/main.py.j2": "src/main.py",
            "src/config.py.j2": "src/config.py",
            "src/health.py.j2": "src/health.py",
            "src/dependencies.py.j2": "src/dependencies.py",
            "src/api/__init__.py.j2": "src/api/__init__.py",
            "src/api/health.py.j2": "src/api/health.py",
            "src/connections/__init__.py.j2": "src/connections/__init__.py",
        }
        
        if config["features"]["redis"]:
            templates["src/connections/redis.py.j2"] = "src/connections/redis.py"
        
        if config["features"]["rabbitmq"]:
            templates["src/connections/rabbitmq.py.j2"] = "src/connections/rabbitmq.py"
        
        if config["features"]["langchain"]:
            templates["src/langchain/__init__.py.j2"] = "src/langchain/__init__.py"
        
        if config["features"]["langfuse"]:
            templates["src/langchain/langfuse_config.py.j2"] = "src/langchain/langfuse_config.py"
        
        for template_name, output_name in templates.items():
            try:
                template_full_path = self.templates_dir / template_name
                if not template_full_path.exists():
                    console.print(f"  [yellow]⚠ Template file not found: {template_name}[/yellow]")
                    continue
                
                content = self.render_template(template_name, config)
                
                output_file = output_path / output_name
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(content)
                console.print(f"  ✓ Generated {output_name}")
                
            except Exception as e:
                console.print(f"  [red]✗ Error when creating {output_name}: {e}[/red]")
                import traceback
                traceback.print_exc()
        
        self.generate_requirements(config, output_path)
        

        self.generate_service_makefile(config, output_path)
        
        console.print(f"\n[bold green]✅ The service was successfully created in the directory'{output_dir}'[/bold green]")
        console.print(f"[bold]Further:[/bold]")
        console.print(f"  1. cd {output_dir}")
        console.print(f"  2. make create-venv")
        console.print(f"  3. make run")
    
    def generate_requirements(self, config: Dict[str, Any], output_path: Path):
        requirements = [
            "fastapi[standard]>=0.109.0",
            "uvicorn[standard]>=0.27.0",
            "pydantic>=2.6.0",
            "pydantic-settings>=2.1.0",
            "python-dotenv>=1.0.0",
            "httpx>=0.26.0",
        ]
        
        if config["features"]["redis"]:
            requirements.extend([
                "redis>=5.0.1",
            ])
        
        if config["features"]["rabbitmq"]:
            requirements.extend([
                "aio-pika>=9.4.0",
            ])
        
        if config["features"]["langchain"]:
            requirements.extend([
                "langchain>=0.1.0",
                "langchain-core>=0.1.0",
            ])
        
        if config["features"]["langfuse"]:
            requirements.extend([
                "langfuse>=2.0.0",
                "opentelemetry-api>=1.20.0",
                "opentelemetry-sdk>=1.20.0",
                "opentelemetry-instrumentation-fastapi>=0.41b0",
                "opentelemetry-instrumentation-httpx>=0.41b0",
                "opentelemetry-exporter-otlp>=1.20.0",
            ])
        
        requirements_file = output_path / "requirements.txt"
        requirements_file.write_text("\n".join(requirements) + "\n")
        console.print("  ✓ Generated requirements.txt")
    
    def generate_service_makefile(self, config: Dict[str, Any], output_path: Path):
        makefile_content = f""".PHONY: help create-venv install run docker-build docker-up docker-down test

PYTHON_VERSION = {config['python_version']}
VENV_NAME ?= .venv
SERVICE_NAME = {config['service_name']}
PORT = {config['port']}

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}}'

create-venv: ## Create a virtual environment
	uv venv $(VENV_NAME) --python $(PYTHON_VERSION)
	@echo "Activate the environment: source $(VENV_NAME)/bin/activate"

install: ## Install  dependencies
	uv pip install -r requirements.txt

run: ## Launch the service locally
	uvicorn src.main:app --host 0.0.0.0 --port $(PORT) --reload

docker-build: ## Build a Docker image
	docker build -t $(SERVICE_NAME) .

docker-up: ## Run with Docker Compose
	docker compose up -d

docker-down: ## Stop Docker Compose
	docker compose down

test: ## Run the tests
	python -m pytest tests/

logs: ## Show logs
	docker-compose logs -f
"""
        
        makefile_path = output_path / "Makefile"
        makefile_path.write_text(makefile_content)
        console.print("  ✓ Makefile Created")

@app.command()
def generate():
    try:
        generator = FastAPIGenerator()
        config = generator.get_service_config()
        
        console.print("\n[bold]Service configuration:[/bold]")
        console.print(f"  Title: {config['service_name']}")
        console.print(f"  Python: {config['python_version']}")
        console.print(f"  Port: {config['port']}")
        console.print(f"  Redis: {'✓' if config['features']['redis'] else '✗'}")
        console.print(f"  RabbitMQ: {'✓' if config['features']['rabbitmq'] else '✗'}")
        console.print(f"  LangChain: {'✓' if config['features']['langchain'] else '✗'}")
        console.print(f"  LangFuse: {'✓' if config['features']['langfuse'] else '✗'}")
        
        if Confirm.ask("\nGenerate a service with this configuration?"):
            generator.generate(config)
        else:
            console.print("[yellow]Generation canceled[/yellow]")
    except KeyboardInterrupt:
        console.print("\n[yellow]The generation was interrupted by the user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Mistake: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    app()