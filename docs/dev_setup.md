# Development Environment Setup

This guide outlines the steps to configure your local development environment. We utilize **`uv`** for high-performance dependency management and Python version control.

## Prerequisites

Before proceeding, ensure you have the following installed on your machine:

* **Visual Studio Code** (Recommended IDE)

## 1. Package Management (`uv`)

We use [`uv`](https://docs.astral.sh/uv/) to manage dependencies and virtual environments.

### Installation

If you do not have `uv` installed, follow the official [installation guide](https://docs.astral.sh/uv/getting-started/installation/) for your operating system.

### Project Setup

Once `uv` is installed, navigate to the project root and sync the environment. This command will install the correct Python version and all required dependencies automatically.

```bash
uv sync
```

> **Note:** For a deeper dive into how we manage dependencies, refer to the [Astral `uv` documentation](https://docs.astral.sh/uv/concepts/projects/dependencies/#dependency-fields).

## 2. VS Code Configuration

This project is optimized for Visual Studio Code. We have configured workspace recommendations to ensure consistent code style and formatting across the team.

### Recommended Extensions

When you open this project in VS Code, you should see a prompt to install "Recommended Extensions." If you missed it, please search for and install the following via the Extensions Marketplace:

* [`ruff`](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff): An extremely fast Python linter and code formatter.
* [`ty`](https://marketplace.visualstudio.com/items?itemName=astral-sh.ty): Type checking support
* [`markdownlint`](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint): Ensures documentation and Markdown files follow standard conventions.
* [`autodocstring`](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring): Generates Python docstrings automatically (configured for Google/NumPy style).
