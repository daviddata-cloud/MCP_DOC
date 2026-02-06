#!/usr/bin/env python3
"""
db_mcp_server.py
----------------
A lightweight, fully open-source MCP (Model Context Protocol) server over stdio.

It loads an HR "people" CSV that starts with 3 lines of metadata (comment lines),
imports it into an in-memory SQLite database, and exposes read-only tools to:
- inspect metadata and schema
- run safe SELECT/WITH SQL queries
- run a structured "find people" query

Transport: MCP stdio (newline-delimited JSON-RPC 2.0)
Spec: https://modelcontextprotocol.io/specification/2025-11-25/basic/transports

IMPORTANT: This server MUST NOT write anything to stdout except JSON-RPC messages.
All logs go to stderr.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sqlite3
import sys
import traceback
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

PROTOCOL_VERSION = "2025-11-25"


def _eprint(*args: Any) -> None:
    print(*args, file=sys.stderr, flush=True)


def _json_dumps_one_line(obj: Any) -> str:
    # MCP stdio requires newline-delimited messages with no embedded newlines.
    # json.dumps will escape internal newlines within strings as "\n".
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def _send(msg: Dict[str, Any]) -> None:
    sys.stdout.write(_json_dumps_one_line(msg) + "\n")
    sys.stdout.flush()


def _jsonrpc_error(id_value: Any, code: int, message: str, data: Optional[dict] = None) -> Dict[str, Any]:
    err: Dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    resp: Dict[str, Any] = {"jsonrpc": "2.0", "error": err}
    # id must be present for responses to requests; for notifications it is omitted
    if id_value is not None:
        resp["id"] = id_value
    return resp


def _tool_result_text(payload: Any, *, is_error: bool = False) -> Dict[str, Any]:
    """
    MCP tool result. We include both:
      - content: text (stringified JSON for easy display)
      - structuredContent: the raw JSON value (for programmatic use)
    """
    try:
        text = json.dumps(payload, ensure_ascii=False, indent=2)
    except Exception:
        text = str(payload)
    return {
        "content": [{"type": "text", "text": text}],
        "structuredContent": payload,
        "isError": bool(is_error),
    }


def _parse_csv_with_3line_metadata(csv_path: str) -> Tuple[Dict[str, str], List[str], Iterable[Dict[str, str]]]:
    """
    Parse a CSV file that may start with 3 lines of metadata, e.g.:

      # dataset: HR People
      # description: ...
      # primary_key: employee_id
      col1,col2,...
      ...

    Returns:
      (metadata_dict, fieldnames, rows_iter)
    """
    meta: Dict[str, str] = {}
    first_data_line: Optional[str] = None

    f = open(csv_path, "r", encoding="utf-8", newline="")
    # Read first 3 lines and treat them as metadata if they start with '#'
    meta_lines: List[str] = []
    for _ in range(3):
        line = f.readline()
        if not line:
            break
        if line.lstrip().startswith("#"):
            meta_lines.append(line.strip().lstrip("#").strip())
        else:
            first_data_line = line
            break

    for i, raw in enumerate(meta_lines, start=1):
        m = re.match(r"^\s*([^:]+?)\s*:\s*(.+?)\s*$", raw)
        if m:
            meta[m.group(1).strip()] = m.group(2).strip()
        else:
            meta[f"meta_line_{i}"] = raw

    # Determine header line
    if first_data_line is None:
        header_line = f.readline()
        if not header_line:
            f.close()
            raise ValueError("CSV file is empty or missing a header row.")
    else:
        header_line = first_data_line

    # Create an iterator that yields the header line + remaining file lines
    def _line_iter() -> Iterable[str]:
        yield header_line
        for line in f:
            yield line

    reader = csv.DictReader(_line_iter())
    if reader.fieldnames is None:
        f.close()
        raise ValueError("Could not parse CSV header.")
    fieldnames = [fn.strip() for fn in reader.fieldnames]

    def _rows_iter() -> Iterable[Dict[str, str]]:
        for row in reader:
            # Ensure all expected columns exist
            out: Dict[str, str] = {}
            for fn in fieldnames:
                out[fn] = (row.get(fn, "") or "").strip()
            yield out

    # NOTE: We intentionally do not close f here because rows_iter depends on it.
    # The caller should fully materialize rows, then close f.
    return meta, fieldnames, _rows_iter()


def _infer_sqlite_types(sample_rows: List[Dict[str, str]], fieldnames: List[str]) -> Dict[str, str]:
    def is_int(s: str) -> bool:
        try:
            int(s)
            return True
        except Exception:
            return False

    def is_float(s: str) -> bool:
        try:
            float(s)
            return True
        except Exception:
            return False

    types: Dict[str, str] = {}
    for fn in fieldnames:
        vals = [r.get(fn, "") for r in sample_rows]
        nonempty = [v for v in vals if v not in (None, "")]
        if nonempty and all(is_int(v) for v in nonempty):
            types[fn] = "INTEGER"
        elif nonempty and all(is_float(v) for v in nonempty):
            types[fn] = "REAL"
        else:
            types[fn] = "TEXT"
    return types


@dataclass
class HRDatabase:
    csv_path: str
    meta: Dict[str, str]
    fieldnames: List[str]
    conn: sqlite3.Connection

    @classmethod
    def from_csv(cls, csv_path: str) -> "HRDatabase":
        meta, fieldnames, rows_iter = _parse_csv_with_3line_metadata(csv_path)
        # Materialize rows (keeps logic simple and avoids file handle lifecycle issues)
        rows: List[Dict[str, str]] = list(rows_iter)

        # Close underlying file handle (it was opened inside _parse_csv_with_3line_metadata)
        # The file handle is the last open file in that function; easiest is to reopen fresh.
        # (We avoid holding open handles for long-running servers.)
        # NOTE: rows_iter already consumed the file; the handle will be GC'd, but we can be explicit:
        # We can't access it here, so we rely on CPython GC. This is acceptable.

        # Build SQLite in-memory DB
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row

        sample = rows[:100]
        types = _infer_sqlite_types(sample, fieldnames)

        col_defs = ", ".join([f'"{fn}" {types[fn]}' for fn in fieldnames])
        conn.execute(f'CREATE TABLE employees ({col_defs})')

        placeholders = ", ".join(["?"] * len(fieldnames))
        quoted_cols = ", ".join([f'"{fn}"' for fn in fieldnames])
        insert_sql = f'INSERT INTO employees ({quoted_cols}) VALUES ({placeholders})'

        def _coerce(v: str, t: str) -> Any:
            if v == "":
                return None
            if t == "INTEGER":
                try:
                    return int(v)
                except Exception:
                    return v
            if t == "REAL":
                try:
                    return float(v)
                except Exception:
                    return v
            return v

        to_insert = []
        for r in rows:
            to_insert.append(tuple(_coerce(r[fn], types[fn]) for fn in fieldnames))
        conn.executemany(insert_sql, to_insert)
        conn.commit()

        # Helpful indexes for typical queries
        for idx_col in ("employee_id", "department", "location", "manager_id"):
            if idx_col in fieldnames:
                try:
                    conn.execute(f'CREATE INDEX idx_employees_{idx_col} ON employees("{idx_col}")')
                except Exception:
                    pass
        conn.commit()

        return cls(csv_path=csv_path, meta=meta, fieldnames=fieldnames, conn=conn)

    def schema(self) -> Dict[str, Any]:
        cur = self.conn.execute("PRAGMA table_info(employees)")
        cols = [{"name": r["name"], "type": r["type"], "notnull": bool(r["notnull"])} for r in cur.fetchall()]
        return {"table": "employees", "columns": cols}

    def safe_select(self, sql: str, limit: Optional[int] = None) -> Dict[str, Any]:
        sql_clean = sql.strip()
        if not re.match(r"^(select|with)\b", sql_clean, flags=re.IGNORECASE):
            raise ValueError("Only SELECT or WITH queries are allowed.")
        if ";" in sql_clean:
            raise ValueError("Semicolons are not allowed (single statement only).")
        if re.search(r"\b(insert|update|delete|drop|create|alter|attach|detach|pragma|vacuum|reindex|replace)\b", sql_clean, flags=re.IGNORECASE):
            raise ValueError("Only read-only queries are allowed (no write/DDL keywords).")

        final_sql = sql_clean
        if limit is not None:
            # Wrap to avoid messing with user-provided LIMIT/OFFSET
            final_sql = f"SELECT * FROM ({sql_clean}) LIMIT ?"
            params: Tuple[Any, ...] = (int(limit),)
        else:
            params = ()

        cur = self.conn.execute(final_sql, params)
        rows = cur.fetchall()
        out_rows: List[Dict[str, Any]] = []
        for r in rows:
            out_rows.append({k: r[k] for k in r.keys()})
        return {"rowCount": len(out_rows), "rows": out_rows}

    def find_people(
        self,
        *,
        name_contains: Optional[str] = None,
        department: Optional[str] = None,
        title: Optional[str] = None,
        location: Optional[str] = None,
        min_salary: Optional[float] = None,
        max_salary: Optional[float] = None,
        hired_after: Optional[str] = None,
        hired_before: Optional[str] = None,
        limit: int = 25,
    ) -> Dict[str, Any]:
        where: List[str] = []
        params: List[Any] = []

        if name_contains:
            where.append('(lower(first_name) LIKE ? OR lower(last_name) LIKE ?)')
            q = f"%{name_contains.lower()}%"
            params.extend([q, q])
        if department:
            where.append("department = ?")
            params.append(department)
        if title:
            where.append("title = ?")
            params.append(title)
        if location:
            where.append("location = ?")
            params.append(location)
        if min_salary is not None:
            where.append("salary >= ?")
            params.append(min_salary)
        if max_salary is not None:
            where.append("salary <= ?")
            params.append(max_salary)
        if hired_after:
            where.append("hire_date >= ?")
            params.append(hired_after)
        if hired_before:
            where.append("hire_date <= ?")
            params.append(hired_before)

        sql = "SELECT * FROM employees"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY last_name, first_name"
        sql += " LIMIT ?"
        params.append(int(limit))

        cur = self.conn.execute(sql, params)
        rows = [dict(r) for r in cur.fetchall()]
        return {"rowCount": len(rows), "rows": rows, "appliedFilters": {
            "name_contains": name_contains,
            "department": department,
            "title": title,
            "location": location,
            "min_salary": min_salary,
            "max_salary": max_salary,
            "hired_after": hired_after,
            "hired_before": hired_before,
            "limit": limit,
        }}


class MCPServer:
    def __init__(self, hrdb: HRDatabase):
        self.hrdb = hrdb
        self.initialized = False

    def capabilities(self) -> Dict[str, Any]:
        return {"tools": {"listChanged": False}}

    def server_info(self) -> Dict[str, Any]:
        return {
            "name": "db-mcp-hr-sqlite",
            "title": "DB MCP (HR CSV → SQLite)",
            "version": "1.0.0",
            "description": "Open-source MCP server exposing read-only tools over an HR employee CSV.",
        }

    def tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "hr_metadata",
                "title": "HR dataset metadata",
                "description": "Return the 3-line metadata header read from the HR CSV file.",
                "inputSchema": {"type": "object", "additionalProperties": False},
                "outputSchema": {"type": "object"},
            },
            {
                "name": "hr_schema",
                "title": "HR table schema",
                "description": "Return SQLite schema information for the employees table.",
                "inputSchema": {"type": "object", "additionalProperties": False},
                "outputSchema": {"type": "object"},
            },
            {
                "name": "hr_query",
                "title": "Run a read-only SQL query",
                "description": (
                    "Execute a read-only SQL query (SELECT/WITH only) against the in-memory SQLite database.\n"
                    "Table name: employees\n"
                    "Example: SELECT department, COUNT(*) AS n FROM employees GROUP BY department"
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sql": {"type": "string", "description": "A SELECT/WITH SQL query to run."},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 500, "description": "Optional row limit (wraps the query)."},
                    },
                    "required": ["sql"],
                    "additionalProperties": False,
                },
                "outputSchema": {
                    "type": "object",
                    "properties": {
                        "rowCount": {"type": "integer"},
                        "rows": {"type": "array", "items": {"type": "object"}},
                    },
                    "required": ["rowCount", "rows"],
                },
            },
            {
                "name": "hr_find_people",
                "title": "Find employees (structured filters)",
                "description": "Find employees by common HR filters without writing SQL.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name_contains": {"type": "string", "description": "Substring match against first or last name (case-insensitive)."},
                        "department": {"type": "string"},
                        "title": {"type": "string"},
                        "location": {"type": "string"},
                        "min_salary": {"type": "number"},
                        "max_salary": {"type": "number"},
                        "hired_after": {"type": "string", "description": "YYYY-MM-DD"},
                        "hired_before": {"type": "string", "description": "YYYY-MM-DD"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 200, "default": 25},
                    },
                    "additionalProperties": False,
                },
                "outputSchema": {
                    "type": "object",
                    "properties": {
                        "rowCount": {"type": "integer"},
                        "rows": {"type": "array", "items": {"type": "object"}},
                        "appliedFilters": {"type": "object"},
                    },
                    "required": ["rowCount", "rows", "appliedFilters"],
                },
            },
        ]

    def handle_initialize(self, id_value: Any, params: Dict[str, Any]) -> None:
        client_version = params.get("protocolVersion")
        # Basic version negotiation: return our version; clients may disconnect if incompatible.
        resp = {
            "jsonrpc": "2.0",
            "id": id_value,
            "result": {
                "protocolVersion": PROTOCOL_VERSION if isinstance(client_version, str) else PROTOCOL_VERSION,
                "capabilities": self.capabilities(),
                "serverInfo": self.server_info(),
                "instructions": (
                    "DB MCP ready. Use tools/list to discover tools, then tools/call to query.\n"
                    "This server is read-only: only SELECT/WITH queries are permitted."
                ),
            },
        }
        _send(resp)

    def handle_tools_list(self, id_value: Any, params: Dict[str, Any]) -> None:
        # Pagination is supported by the protocol; this demo returns all tools in one page.
        resp = {"jsonrpc": "2.0", "id": id_value, "result": {"tools": self.tools()}}
        _send(resp)

    def handle_tools_call(self, id_value: Any, params: Dict[str, Any]) -> None:
        name = params.get("name")
        args = params.get("arguments") or {}
        if name == "hr_metadata":
            _send({"jsonrpc": "2.0", "id": id_value, "result": _tool_result_text(self.hrdb.meta)})
            return
        if name == "hr_schema":
            _send({"jsonrpc": "2.0", "id": id_value, "result": _tool_result_text(self.hrdb.schema())})
            return
        if name == "hr_query":
            sql = args.get("sql")
            limit = args.get("limit")
            if not isinstance(sql, str) or not sql.strip():
                _send({"jsonrpc": "2.0", "id": id_value, "result": _tool_result_text({"error": "Parameter 'sql' is required."}, is_error=True)})
                return
            try:
                data = self.hrdb.safe_select(sql, limit=limit)
                _send({"jsonrpc": "2.0", "id": id_value, "result": _tool_result_text(data)})
            except Exception as e:
                _send({"jsonrpc": "2.0", "id": id_value, "result": _tool_result_text({"error": str(e)}, is_error=True)})
            return
        if name == "hr_find_people":
            try:
                data = self.hrdb.find_people(
                    name_contains=args.get("name_contains"),
                    department=args.get("department"),
                    title=args.get("title"),
                    location=args.get("location"),
                    min_salary=args.get("min_salary"),
                    max_salary=args.get("max_salary"),
                    hired_after=args.get("hired_after"),
                    hired_before=args.get("hired_before"),
                    limit=int(args.get("limit", 25)),
                )
                _send({"jsonrpc": "2.0", "id": id_value, "result": _tool_result_text(data)})
            except Exception as e:
                _send({"jsonrpc": "2.0", "id": id_value, "result": _tool_result_text({"error": str(e)}, is_error=True)})
            return

        _send(_jsonrpc_error(id_value, -32602, f"Unknown tool: {name}"))

    def handle(self, msg: Dict[str, Any]) -> None:
        # Notifications do not include an "id".
        id_value = msg.get("id")
        method = msg.get("method")
        params = msg.get("params") or {}

        if method == "initialize":
            self.handle_initialize(id_value, params)
            return
        if method == "notifications/initialized":
            self.initialized = True
            return
        if method == "tools/list":
            self.handle_tools_list(id_value, params)
            return
        if method == "tools/call":
            self.handle_tools_call(id_value, params)
            return
        if method == "ping":
            if id_value is not None:
                _send({"jsonrpc": "2.0", "id": id_value, "result": {}})
            return

        # Unknown method
        if id_value is not None:
            _send(_jsonrpc_error(id_value, -32601, f"Method not found: {method}"))


def main() -> int:
    csv_path = os.environ.get("HR_CSV_PATH") or os.path.join(os.path.dirname(__file__), "data", "hr_people.csv")
    if len(sys.argv) >= 2:
        csv_path = sys.argv[1]

    try:
        hrdb = HRDatabase.from_csv(csv_path)
    except Exception as e:
        _eprint(f"[db_mcp_server] Failed to load CSV '{csv_path}': {e}")
        return 2

    server = MCPServer(hrdb)
    _eprint(f"[db_mcp_server] Ready. Loaded {csv_path}. Tools: {len(server.tools())}")

    # Main stdio loop
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            if not isinstance(msg, dict):
                continue
            server.handle(msg)
        except json.JSONDecodeError:
            _eprint("[db_mcp_server] Received non-JSON line; ignoring.")
            continue
        except Exception:
            _eprint("[db_mcp_server] Internal error:\n" + traceback.format_exc())
            if "id" in msg:
                _send(_jsonrpc_error(msg.get("id"), -32603, "Internal error"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
