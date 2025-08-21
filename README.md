# Project Pantheon

**Project Pantheon** is a robust and extensible command and governance system designed for orchestrating and managing complex multi-agent AI systems. It provides a comprehensive framework for defining, executing, and evaluating sophisticated missions, enabling seamless integration of diverse AI agents and Large Language Models (LLMs).

[![Pantheon Red Team Evaluation Demo](./docs/images/pantheon.gif)](./docs/images/pantheon.gif)

## Why Project Pantheon?

In the rapidly evolving landscape of AI, managing and coordinating multiple intelligent agents can be challenging. Project Pantheon addresses this by offering:

*   **Centralized Control:** Define and manage complex multi-agent workflows from a single, intuitive configuration.
*   **Economic Governance:** Implement cost-aware decision-making for LLM usage, ensuring efficient resource allocation.
*   **Mission-Driven Operations:** Structure AI tasks into clear, executable missions, complete with agents, tools, and evaluation criteria.
*   **Flexibility & Extensibility:** Easily integrate new LLM providers, custom agents, specialized tools, and diverse workflows.
*   **Robust Evaluation:** Test agent performance against predefined scenarios, important for developing reliable and safe AI systems.

## Table of Contents

*   [Key Features](#key-features)
*   [Getting Started](#getting-started)
    *   [Prerequisites](#prerequisites)
    *   [Installation](#installation)
    *   [Environment Variables](#environment-variables)
*   [Usage](#usage)
    *   [Running a Mission](#running-a-mission)
    *   [Running an Evaluation](#running-an-evaluation)
*   [Configuration](#configuration)
    *   [Missions](#missions)
    *   [Agents](#agents)
    *   [LLM Providers](#llm-providers)
    *   [Workflows](#workflows)
    *   [Tools](#tools)
*   [Project Structure](#project-structure)
*   [Contributing](#contributing)
    *   [How to Contribute](#how-to-contribute)
    *   [Reporting Bugs](#reporting-bugs)
    *   [Feature Requests](#feature-requests)
    [Code Style](#code-style)
    *   [Testing](#testing)
*   [License](#license)

## Key Features

*   **Mission-driven:** Define complex tasks and workflows using simple YAML configuration files.
*   **Agent Agnostic:** Easily integrate different types of AI agents and LLM providers (e.g., Google Gemini, OpenAI, Hugging Face models via Langchain).
*   **Governance Layer:** Monitor and control agent behavior with features like an economic governor to manage costs and permissions.
*   **Extensible:** A modular architecture that allows for the addition of new agents, tasks, tools, and workflows (e.g., CrewAI, LangGraph).
*   **Evaluation Framework:** Test and evaluate the performance of your multi-agent systems against adversarial scenarios.
*   **Long-Term Memory:** Enables the system to learn from past missions and improve its performance over time using vector stores (e.g., FAISS).

## Getting Started

### Prerequisites

*   Python 3.11+
*   An API key for your chosen LLM provider (e.g., Google Gemini or OpenAI).

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/msyber/pantheon.git
    cd pantheon
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -e .
    ```

### Environment Variables

Copy the `.env.example` file to a new file named `.env` and populate it with your LLM API keys:

```bash
cp .env.example .env
```

Open the `.env` file and add your LLM provider's API key(s). For example:

```
GOOGLE_API_KEY="your-google-api-key"
OPENAI_API_KEY="your-openai-api-key"
# Add other API keys as needed, e.g., for Hugging Face
```

## Usage

### Running a Mission

To run a predefined mission, use the `src/main.py` script, specifying the `mission_id` and `llm_provider`. Mission configurations are located in `config/missions/`.

```bash
python -m src.main --mission_id <mission_name> --llm_provider <provider_name>
```

**Examples:**

*   To run the `hunt_suspicious_ip_001` mission with Google Gemini:
    ```bash
    python -m src.main --mission_id hunt_suspicious_ip_001 --llm_provider google_gemini
    ```
*   To run the `contain_ransomware_incident_001` mission with OpenAI:
    ```bash
    python -m src.main --mission_id contain_ransomware_incident_001 --llm_provider openai
    ```

### Running an Evaluation

The `src/run_evaluation.py` script is used to execute predefined adversarial missions and evaluate the system's performance. This is important for testing the robustness and effectiveness of your multi-agent setups.

```bash
python -m src.run_evaluation
```

## Configuration

Project Pantheon's behavior is highly configurable through YAML files located in the `config/` directory. This modular approach allows for easy customization and extension.

*   **`config/missions/`**: Defines the overall missions. Each mission specifies the agents involved, the tasks they need to perform, the workflow to follow, and any specific tools required.
    *   *Example:* `hunt_suspicious_ip_001.yaml` might define a mission for a cybersecurity team to investigate a suspicious IP address.
*   **`config/agents/`**: Configures individual AI agents. This includes their roles, backstories, goals, and the specific tools they have access to.
    *   *Example:* `cyber_security_team.yaml` could define roles like "Threat Analyst" or "Incident Responder."
*   **`config/llm_providers/`**: Manages the configurations for different Large Language Model providers. Here you define the model names, API endpoints, and any provider-specific settings.
    *   *Example:* `google_gemini.yaml` or `openai.yaml` for configuring API keys and model versions.
*   **`config/workflows/`**: Defines the execution flow for tasks within a mission. Pantheon supports various workflow patterns, including sequential, parallel, and more complex graph-based workflows (e.g., CrewAI, LangGraph).
    *   *Example:* `sequential_investigation.yaml` might outline a step-by-step process for an investigation.
*   **`config/tools/`**: Specifies the tools that agents can utilize. These can be external APIs, custom scripts, or internal functions that extend the agents' capabilities.
    *   *Example:* `cyber_tools.yaml` could list tools for network scanning, log analysis, or threat intelligence lookups.

## Project Structure

```
pantheon/
├── config/                # YAML configuration files for missions, agents, LLMs, workflows, and tools.
├── data/                  # Stores raw and processed data, such as suspicious logs or evaluation results.
├── evaluation/            # Contains scripts and configurations for evaluating multi-agent system performance.
├── src/                   # Core source code for the Pantheon system.
│   ├── agents/            # Definitions and implementations of various AI agents.
│   ├── config/            # Internal configuration loading and management utilities.
│   ├── evaluation/        # Logic for running and analyzing system evaluations.
│   ├── governance/        # Economic governor and permission management for agents.
│   ├── identity/          # Manages agent identities and permissions.
│   ├── llm_providers/     # Interfaces for integrating different Large Language Model providers.
│   ├── memory/            # Implementations for long-term memory and knowledge retention (e.g., vector stores).
│   ├── observability/     # Logging and monitoring components.
│   ├── orchestrators/     # Core logic for orchestrating agent interactions and workflows.
│   ├── tasks/             # Definitions of individual tasks that agents can perform.
│   ├── tools/             # Implementations of tools available to agents.
│   ├── workflows/         # Different workflow patterns (e.g., CrewAI, LangGraph) for mission execution.
│   ├── main.py            # Entry point for running missions.
│   └── run_evaluation.py  # Script for executing system evaluations.
├── .env.example           # Example environment variables file.
├── pyproject.toml         # Project metadata and Python dependency management (Poetry/Ruff).
├── README.md              # This documentation file.
├── .gitignore             # Specifies intentionally untracked files to ignore.
├── output.log             # Log file for system output.
├── logs/                  # Directory for application logs.
└── .venv/                 # Python virtual environment.
```

## Contributing

We welcome contributions to Project Pantheon! Whether it's bug fixes, new features, or improved documentation, your help is appreciated.

### How to Contribute

1.  **Fork the repository.**
2.  **Clone your forked repository:**
    ```bash
    git clone https://github.com/your-username/pantheon.git
    cd pantheon
    ```
3.  **Create a new branch** for your feature or bug fix:
    ```bash
    git checkout -b feature/your-feature-name
    ```
4.  **Make your changes.**
5.  **Ensure your code adheres to the project's style guidelines** (see [Code Style](#code-style)).
6.  **Write and run tests** to ensure your changes work as expected and don't introduce regressions (see [Testing](#testing)).
7.  **Commit your changes** with a clear and concise commit message.
8.  **Push your branch** to your forked repository.
9.  **Open a Pull Request** to the `main` branch of the original repository.

### Reporting Bugs

If you find a bug, please open an issue on the [GitHub Issues page](https://github.com/msyber/pantheon/issues). Provide a clear description of the bug, steps to reproduce it, and expected behavior.

### Feature Requests

Have an idea for a new feature? Open an issue on the [GitHub Issues page](https://github.com/msyber/pantheon/issues) to discuss it.

### Code Style

Project Pantheon uses `ruff` for code formatting and linting. Please ensure your code is formatted correctly before submitting a pull request. You can run `ruff check . --fix` to automatically fix most issues.

### Testing

Currently, there are no automated tests explicitly defined in the project. If you are adding new features or fixing bugs, it is highly recommended to implement corresponding tests to ensure functionality and prevent regressions.

Common Python testing frameworks include `pytest`. If tests were implemented, you would typically run them using a command like:

```bash
# Example: If using pytest
# pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/msyber/pantheon/blob/main/LICENSE) file for details.