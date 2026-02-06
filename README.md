# DB MCP (HR CSV → SQLite) — Open Source Reference

This folder contains a **fully open-source** Model Context Protocol (MCP) server implementation that:

- Loads an HR “people” CSV file
- Reads **3 lines of metadata** at the top of the CSV (comment lines starting with `#`)
- Imports the CSV into an **in-memory SQLite** database
- Exposes **read-only MCP tools** over **stdio** (newline-delimited JSON-RPC 2.0)

No Claude Desktop setup is required. A small Python client is included for testing.

## Files

- `db_mcp_server.py` — MCP server (stdio)
- `db_mcp_client.py` — simple MCP stdio client for testing
- `data/hr_people.csv` — sample HR CSV with 3-line metadata header

## Run the server

```bash
python db_mcp_server.py
```

Optionally pass a custom CSV path:

```bash
python db_mcp_server.py /path/to/your/hr_people.csv
```

Or set an environment variable:

```bash
HR_CSV_PATH=/path/to/your/hr_people.csv python db_mcp_server.py
```

## Test with the included client (recommended)

```bash
python db_mcp_client.py
```

You should see:

- `initialize` handshake
- `tools/list`
- a sample SQL query result
- an interactive prompt to run more `SELECT` queries

## Tools exposed

- `hr_metadata` — returns the 3-line metadata header as a JSON object
- `hr_schema` — returns the SQLite schema for table `employees`
- `hr_query` — execute **read-only** `SELECT`/`WITH` SQL queries
- `hr_find_people` — structured search without writing SQL

## CSV metadata format (first 3 lines)

Example:

```text
# dataset: HR People
# description: Synthetic employee roster for MCP demo (no real PII)
# primary_key: employee_id
employee_id,first_name,last_name,...
```

Metadata lines are parsed as `key: value`. If a line is not `key: value`, it is stored as `meta_line_1`, `meta_line_2`, etc.

## Notes for sharing

- Everything here is standard-library Python (SQLite + CSV).
- The demo data is synthetic (no real PII).
- The server writes **only JSON-RPC** to stdout. Logs go to stderr (safe for stdio MCP).
