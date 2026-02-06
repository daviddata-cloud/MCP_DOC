#!/usr/bin/env python3
"""
doc_mcp_client.py
-----------------
A tiny MCP stdio client to test the Documentation MCP server WITHOUT Claude/any proprietary host.

Usage:
  # Interactive mode (original)
  python doc_mcp_client.py
  
  # Non-interactive JSON search mode
  python doc_mcp_client.py --search "diabetes" --top-k 5
  
  # Batch JSON search mode (multiple queries)
  python doc_mcp_client.py --batch-search queries.json
  
  # Output to JSON file
  python doc_mcp_client.py --search "diabetes" --output results.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
from typing import Any, Dict, Optional, List

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


def initialize_client(client: MCPStdioClient, verbose: bool = False) -> None:
    """Initialize the MCP client connection."""
    init = client.request(
        "initialize",
        {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "doc-mcp-cli", "version": "2.0.0"},
        },
    )
    if verbose:
        print("Initialize response:", file=sys.stderr)
        print(json.dumps(init, indent=2), file=sys.stderr)
    client.notify("notifications/initialized")


def search_documents(client: MCPStdioClient, query: str, top_k: int = 5) -> Dict[str, Any]:
    """Perform a document search and return results."""
    response = client.request(
        "tools/call",
        {
            "name": "doc_search",
            "arguments": {
                "query": query,
                "top_k": top_k
            }
        }
    )
    return response


def batch_search(client: MCPStdioClient, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Perform multiple searches and return all results."""
    results = []
    for query_spec in queries:
        query = query_spec.get("query", "")
        top_k = query_spec.get("top_k", 5)
        
        result = {
            "query": query,
            "top_k": top_k,
            "response": search_documents(client, query, top_k)
        }
        results.append(result)
    
    return results


def list_resources(client: MCPStdioClient) -> Dict[str, Any]:
    """List all available resources."""
    return client.request("resources/list", {})


def read_resource(client: MCPStdioClient, uri: str) -> Dict[str, Any]:
    """Read a specific resource by URI."""
    return client.request("resources/read", {"uri": uri})


def interactive_mode(client: MCPStdioClient) -> None:
    """Run the client in interactive mode."""
    print("\n=== Interactive Mode ===")
    print("Commands:")
    print("  search <query>  - Search documents")
    print("  list            - List all resources")
    print("  read <uri>      - Read a specific resource")
    print("  exit/quit       - Exit interactive mode")
    print()
    
    while True:
        try:
            command = input("DOC-MCP> ").strip()
        except EOFError:
            break
        
        if not command:
            continue
        
        if command.lower() in ("exit", "quit"):
            break
        
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        
        if cmd == "search":
            if len(parts) < 2:
                print("Usage: search <query>")
                continue
            query = parts[1]
            resp = search_documents(client, query, top_k=5)
            print(json.dumps(resp, indent=2))
        
        elif cmd == "list":
            resp = list_resources(client)
            print(json.dumps(resp, indent=2))
        
        elif cmd == "read":
            if len(parts) < 2:
                print("Usage: read <uri>")
                continue
            uri = parts[1]
            resp = read_resource(client, uri)
            # Show first 500 chars of content
            text = resp.get("result", {}).get("contents", [{}])[0].get("text", "")
            print(f"Resource: {uri}")
            print(text[:500])
            if len(text) > 500:
                print(f"\n... (truncated, total {len(text)} chars)")
        
        else:
            print(f"Unknown command: {cmd}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Documentation MCP Client - Interactive and JSON-based search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python doc_mcp_client.py
  
  # Single search query
  python doc_mcp_client.py --search "diabetes treatment" --top-k 10
  
  # Batch search from JSON file
  python doc_mcp_client.py --batch-search queries.json
  
  # Output to JSON file
  python doc_mcp_client.py --search "hypertension" --output results.json
  
  # List all resources
  python doc_mcp_client.py --list-resources
  
  # Read specific resource
  python doc_mcp_client.py --read-resource "doc://policy.md"

Batch search JSON format (queries.json):
  [
    {"query": "diabetes", "top_k": 5},
    {"query": "hypertension", "top_k": 10},
    {"query": "medication guidelines", "top_k": 3}
  ]
        """
    )
    
    # Mode selection
    parser.add_argument(
        "--search", "-s",
        type=str,
        help="Single search query (non-interactive mode)"
    )
    
    parser.add_argument(
        "--top-k", "-k",
        type=int,
        default=5,
        help="Number of top results to return (default: 5)"
    )
    
    parser.add_argument(
        "--batch-search", "-b",
        type=str,
        help="Path to JSON file with multiple search queries"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output results to JSON file instead of stdout"
    )
    
    parser.add_argument(
        "--list-resources",
        action="store_true",
        help="List all available resources"
    )
    
    parser.add_argument(
        "--read-resource",
        type=str,
        help="Read a specific resource by URI"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output (show initialization details)"
    )
    
    parser.add_argument(
        "--server",
        type=str,
        default=None,
        help="Path to doc_mcp_server.py (auto-detected if not provided)"
    )
    
    args = parser.parse_args()
    
    # Determine server path
    if args.server:
        server_py = args.server
    else:
        server_py = os.path.join(os.path.dirname(__file__), "doc_mcp_server.py")
    
    if not os.path.exists(server_py):
        print(f"Error: Server not found at {server_py}", file=sys.stderr)
        return 1
    
    # Start client
    cmd = [sys.executable, server_py]
    client = MCPStdioClient(cmd)
    
    try:
        # Initialize
        initialize_client(client, verbose=args.verbose)
        
        # Determine mode
        output_data = None
        
        if args.list_resources:
            # List resources mode
            output_data = list_resources(client)
        
        elif args.read_resource:
            # Read resource mode
            output_data = read_resource(client, args.read_resource)
        
        elif args.search:
            # Single search mode
            output_data = search_documents(client, args.search, args.top_k)
        
        elif args.batch_search:
            # Batch search mode
            if not os.path.exists(args.batch_search):
                print(f"Error: Batch file not found: {args.batch_search}", file=sys.stderr)
                return 1
            
            with open(args.batch_search, 'r', encoding='utf-8') as f:
                queries = json.load(f)
            
            if not isinstance(queries, list):
                print("Error: Batch search file must contain a JSON array", file=sys.stderr)
                return 1
            
            output_data = {
                "batch_results": batch_search(client, queries),
                "total_queries": len(queries)
            }
        
        else:
            # Interactive mode (default)
            interactive_mode(client)
            return 0
        
        # Handle output
        if output_data:
            if args.output:
                # Write to file
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=2, ensure_ascii=False)
                print(f"Results written to {args.output}", file=sys.stderr)
            else:
                # Print to stdout
                print(json.dumps(output_data, indent=2, ensure_ascii=False))
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        client.close()
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
