#!/usr/bin/env python3
"""
db_mcp_client.py
----------------
A tiny MCP stdio client you can use to test the DB MCP server WITHOUT Claude/any proprietary host.

Usage:
  python db_mcp_client.py
  python db_mcp_client.py --csv ./data/hr_people.csv
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from typing import Any, Dict, Optional


PROTOCOL_VERSION = "2025-11-25"


def _json_dumps_one_line(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


class MCPStdioClient:
    def __init__(self, command: list[str]):
        self.proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        assert self.proc.stdin and self.proc.stdout and self.proc.stderr
        self._next_id = 1
        self._stderr_thread = threading.Thread(target=self._drain_stderr, daemon=True)
        self._stderr_thread.start()

    def _drain_stderr(self) -> None:
        assert self.proc.stderr
        for line in self.proc.stderr:
            sys.stderr.write(line)
            sys.stderr.flush()

    def send(self, msg: Dict[str, Any]) -> None:
        assert self.proc.stdin
        self.proc.stdin.write(_json_dumps_one_line(msg) + "\n")
        self.proc.stdin.flush()

    def request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        req_id = self._next_id
        self._next_id += 1
        self.send({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params or {}})

        # Wait for matching response
        assert self.proc.stdout
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("Server exited or closed stdout.")
            msg = json.loads(line)
            if isinstance(msg, dict) and msg.get("id") == req_id:
                return msg

    def notify(self, method: str, params: Optional[Dict[str, Any]] = None) -> None:
        self.send({"jsonrpc": "2.0", "method": method, "params": params or {}})

    def close(self) -> None:
        try:
            if self.proc.stdin:
                self.proc.stdin.close()
        except Exception:
            pass
        try:
            self.proc.terminate()
        except Exception:
            pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=os.path.join(os.path.dirname(__file__), "data", "hr_people.csv"))
    args = ap.parse_args()

    server_py = os.path.join(os.path.dirname(__file__), "db_mcp_server.py")
    cmd = [sys.executable, server_py, args.csv]

    client = MCPStdioClient(cmd)
    try:
        init = client.request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},  # this demo client offers no optional features
                "clientInfo": {"name": "db-mcp-cli", "version": "1.0.0"},
            },
        )
        print("Initialize response:")
        print(json.dumps(init, indent=2))

        client.notify("notifications/initialized")

        tools = client.request("tools/list", {})
        print("\nTools:")
        print(json.dumps(tools, indent=2))

        # Sample query
        sample = client.request(
            "tools/call",
            {"name": "hr_query", "arguments": {"sql": "SELECT department, COUNT(*) AS n FROM employees GROUP BY department ORDER BY n DESC"}},
        )
        print("\nSample hr_query result:")
        print(json.dumps(sample, indent=2))

        # Interactive loop
        print("\nInteractive mode. Type SQL (SELECT ...) or 'exit'.")
        while True:
            try:
                sql = input("SQL> ").strip()
            except EOFError:
                break
            if not sql:
                continue
            if sql.lower() in ("exit", "quit"):
                break
            resp = client.request("tools/call", {"name": "hr_query", "arguments": {"sql": sql, "limit": 50}})
            print(json.dumps(resp, indent=2))
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
