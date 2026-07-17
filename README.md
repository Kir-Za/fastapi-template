# FastAPI Service Generator

A CLI tool for scaffolding production-ready FastAPI microservices with containerization support, and optional integrations with Redis, RabbitMQ, LangChain, and LangFuse. A lightweight version of the magnificent https://github.com/cookiecutter/cookiecutter

## Features

- 🚀 **Interactive CLI** - Step-by-step service configuration wizard
- 🐳 **Docker Ready** - Automatic Dockerfile and Docker Compose generation
- 📦 **12-Factor App** - Environment-based configuration with pydantic-settings
- ❤️ **Health Checks** - Built-in health check API with component status monitoring
- 🔄 **Async Support** - Fully asynchronous architecture
- 🎯 **Modular Design** - Pick only the components you need

### Supported Integrations

- 📦 **Redis** - Caching and session storage
- 🐰 **RabbitMQ** - Message queuing and event-driven architecture
- 🔗 **LangChain** - LLM framework integration
- 📊 **LangFuse** - LLM observability and monitoring with OpenTelemetry

## Quick Start

### Installation

```bash
# Clone the repository 
cd fastapi-generator

# Create virtual environment
make create-venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
make install-deps