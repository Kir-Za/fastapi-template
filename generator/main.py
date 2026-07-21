#!/usr/bin/env python3
"""
FastAPI Service Generator
Creates production-ready FastAPI microservices with 12-factor app methodology
"""

import os
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
    """Generator for FastAPI microservices with optional Redis, RabbitMQ, and LangFuse support."""
    
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
        """Interactive dialog to configure the service."""
        console.print(Panel.fit(
            "[bold cyan]🚀 FastAPI Service Generator[/bold cyan]\n"
            "[dim]Create a microservice with 12-factor app architecture[/dim]\n"
            "[dim]Supports: Redis, RabbitMQ, LangFuse[/dim]"
        ))
        
        config = {
            "service_name": Prompt.ask(
                "Enter service name",
                default="fastapi-service"
            ),
            "python_version": Prompt.ask(
                "Python version",
                default="3.12"
            ),
            "port": Prompt.ask(
                "Service port",
                default="8000"
            ),
            "features": {}
        }
        
        # Component selection
        console.print("\n[bold]Select components for the service:[/bold]")
        
        config["features"]["redis"] = Confirm.ask(
            "📦 Enable Redis?",
            default=True
        )
        
        config["features"]["rabbitmq"] = Confirm.ask(
            "🐰 Enable RabbitMQ?",
            default=False
        )
        
        if config["features"]["rabbitmq"]:
            config["rabbitmq_vhost"] = Prompt.ask(
                "RabbitMQ Virtual Host",
                default="/"
            )
            config["rabbitmq_queue_in"] = Prompt.ask(
                "Input queue name",
                default=f"{config['service_name']}.input"
            )
            config["rabbitmq_queue_out"] = Prompt.ask(
                "Output queue name",
                default=f"{config['service_name']}.output"
            )
        
        config["features"]["langfuse"] = Confirm.ask(
            "📊 Enable LangFuse (observability)?",
            default=False
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
        """Render a Jinja2 template with error handling."""
        try:
            template = self.env.get_template(template_path)
            return template.render(**config)
        except TemplateNotFound:
            console.print(f"[red]Template not found: {template_path}[/red]")
            raise
    
    def generate(self, config: Dict[str, Any], output_dir: str = "generated_service"):
        """Generate the service project based on configuration."""
        output_path = Path(output_dir)
        
        console.print(f"\n[bold green]Generating service '{config['service_name']}'...[/bold green]")
        
        # Create directory structure
        directories = [
            output_path,
            output_path / "src",
            output_path / "src" / "api",
            output_path / "src" / "connections",
            output_path / "tests",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            console.print(f"  [dim]Created directory: {directory}[/dim]")
        
        # Template mapping: {template_path: output_path}
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
        
        # Add templates based on selected features
        if config["features"]["redis"]:
            templates["src/connections/redis.py.j2"] = "src/connections/redis.py"
        
        if config["features"]["rabbitmq"]:
            templates["src/connections/rabbitmq.py.j2"] = "src/connections/rabbitmq.py"
            templates["src/connections/schemas.py.j2"] = "src/connections/schemas.py"
            templates["src/connections/handlers.py.j2"] = "src/connections/handlers.py"
            templates["src/connections/consumer.py.j2"] = "src/connections/consumer.py"
            templates["src/connections/publisher.py.j2"] = "src/connections/publisher.py"
            templates["src/connections/init_publisher.py.j2"] = "src/connections/init_publisher.py"
        
        if config["features"]["langfuse"]:
            templates["src/connections/langfuse_config.py.j2"] = "src/connections/langfuse_config.py"
        
        # Generate files from templates
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
                console.print(f"  ✓ Created {output_name}")
                
            except Exception as e:
                console.print(f"  [red]✗ Error creating {output_name}: {e}[/red]")
                import traceback
                traceback.print_exc()
        
        # Generate requirements.txt
        self.generate_requirements(config, output_path)
        
        # Generate Makefile for the service
        self.generate_service_makefile(config, output_path)
        
        console.print(f"\n[bold green]✅ Service successfully created in '{output_dir}'[/bold green]")
        console.print(f"[bold]Next steps:[/bold]")
        console.print(f"  1. cd {output_dir}")
        console.print(f"  2. make create-venv")
        console.print(f"  3. make run")
    
    def generate_requirements(self, config: Dict[str, Any], output_path: Path):
        """Generate requirements.txt with appropriate dependencies."""
        requirements = [
            "fastapi>=0.109.0",
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
        
        if config["features"]["langfuse"]:
            requirements.extend([
                "langfuse>=2.0.0",
            ])
        
        requirements_file = output_path / "requirements.txt"
        requirements_file.write_text("\n".join(requirements) + "\n")
        console.print("  ✓ Created requirements.txt")
    
    def generate_service_makefile(self, config: Dict[str, Any], output_path: Path):
        """Generate Makefile for the created service."""
        makefile_content = f""".PHONY: help create-venv install run docker-build docker-up docker-down test

PYTHON_VERSION = {config['python_version']}
VENV_NAME ?= .venv
SERVICE_NAME = {config['service_name']}
PORT = {config['port']}

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {{FS = ":.*?## "}}; {{printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}}'

create-venv: ## Create virtual environment
	uv venv $(VENV_NAME) --python $(PYTHON_VERSION)
	@echo "Activate the environment: source $(VENV_NAME)/bin/activate"

install: ## Install dependencies
	uv pip install -r requirements.txt

run: ## Run service locally
	uvicorn src.main:app --host 0.0.0.0 --port $(PORT) --reload

docker-build: ## Build Docker image
	docker build -t $(SERVICE_NAME) .

docker-up: ## Start with Docker Compose
	docker-compose up -d

docker-down: ## Stop Docker Compose
	docker-compose down

test: ## Run tests
	python -m pytest tests/

logs: ## Show logs
	docker-compose logs -f
"""
        
        makefile_path = output_path / "Makefile"
        makefile_path.write_text(makefile_content)
        console.print("  ✓ Created Makefile")


@app.command()
def generate():
    """Generate a new FastAPI service."""
    try:
        generator = FastAPIGenerator()
        config = generator.get_service_config()
        
        console.print("\n[bold]Service configuration:[/bold]")
        console.print(f"  Name: {config['service_name']}")
        console.print(f"  Python: {config['python_version']}")
        console.print(f"  Port: {config['port']}")
        console.print(f"  Redis: {'✓' if config['features']['redis'] else '✗'}")
        console.print(f"  RabbitMQ: {'✓' if config['features']['rabbitmq'] else '✗'}")
        console.print(f"  LangFuse: {'✓' if config['features']['langfuse'] else '✗'}")
        
        if Confirm.ask("\nGenerate service with this configuration?"):
            generator.generate(config)
        else:
            console.print("[yellow]Generation cancelled[/yellow]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Generation interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    app()