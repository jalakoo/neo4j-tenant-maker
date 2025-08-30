# Neo4j Tenant Maker

This tool helps you create tenants and databases within a Neo4j Enterprise Edition instance. Note this will not work with Aura databases.

# Prerequisites
- Python 3.13
- uv (https://docs.astral.sh/uv/)

# Setup
1. Download or clone this repo
2. Install dependencies:
```bash
uv sync
```
3. Copy `.env.sample` to `.env` and fill in your connection settings

# Usage

Adding users:
```bash
uv run python main.py add user1@example.com user2@example.org
```

Removing users:
```bash
uv run python main.py remove user1@example.com user2@example.org
```

