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

Adding single users:
```bash
uv run python main.py add --emails user1@example.com user2@example.org
```

Removing single users:
```bash
uv run python main.py remove --emails user1@example.com user2@example.org
```

Adding users from a CSV file:
```bash
uv run python main.py add --csv sample.csv
```

Removing users from a CSV file:
```bash
uv run python main.py remove --csv sample.csv
```

## Generating a CSV file of mock emails
For testing purposes, you can generate a CSV file of mock emails using the `generate_emails.py` script. Below example generates 10 random emails and saves to `emails.csv` (default filename):
```bash
uv run python generate_emails.py 10 -o emails.csv
```
