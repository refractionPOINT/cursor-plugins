#!/usr/bin/env python3
"""Check this plugin's tool references against the hosted LimaCharlie MCP server.

Run before every release:  python3 scripts/check_mcp_tools.py

It verifies that:
  1. every tool in the read-only connection's X-MCP-Tools allowlist exists on
     the server (the server rejects the whole list if one name is unknown,
     which would take the read-only connection down);
  2. the allowlist matches the reviewed read-only set in
     scripts/reviewed_tools.json, and every tool on the server has been
     reviewed (classified read_only or excluded), so a new server tool can
     never slip onto the read-only connection unreviewed;
  3. the allowlist contains no tool whose name marks it as a write, a
     credential read, a URL fetch or a file write (a second, name-based net);
  4. every tool or parameter name the skills mention exists on the server;
  5. every connection has its own URL (Grok Bot and Cursor keep only one
     connection per URL, so a shared one silently drops the other).

Only `tools/list` is called, which needs no credentials and changes nothing.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
READ_ONLY_SERVER = "limacharlie"

# Name patterns that must never be on the read-only connection.
FORBIDDEN_PATTERNS = [
    r"^(set|delete|create|add|remove|update|merge|import|rename|reset|dismiss|"
    r"enable|disable|subscribe|unsubscribe|start|terminate|rekey|upgrade|mass)_",
    r"^(isolate|rejoin)_network$", r"^(seal|unseal)_sensor$", r"^task_sensor$",
    r"^reliable_tasking$", r"^memory_dump_sensor$", r"^extension_request$",
    r"^lc_call_tool$", r"^replay_dr_rule$", r"^collect_velociraptor_artifact$",
    r"^vulnerability_(scan|set_|bulk_|reset_)",
    r"^cloudsec_(set_|bulk_|dismiss_|restore_|ingest_|test_|code_scan|code_autofix|code_provenance_push)",
    # Reads that return credentials or configs that can embed them.
    r"^get_secret$", r"installation_key", r"^list_outputs$", r"^get_org_value$",
    r"^(get|list)_(cloud_sensors?|external_adapters?|extension_configs?)$",
    r"^get_extension_config$", r"^(get_rule|list_rules)$",
    # URL fetches, file writes, stored ARLs and other agents' histories.
    r"^resolve_arl$", r"^get_payload$", r"^yara_scan_", r"^(get|list)_yara_(sources?|rules?)$",
    r"^(get|list)_ai_(chat|session)", r"^request_feedback_",
]


# snake_case words the skills use that are values, not tools or parameters.
NON_TOOL_WORDS = {
    "artifact_event", "file_hash", "file_name", "file_path", "package_name", "service_name",
}


def live_tools(url: str) -> tuple[set[str], set[str]]:
    """Return (tool names, parameter names) from the server's tools/list."""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).encode()
    request = urllib.request.Request(url, data=body, headers={"content-type": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        tools = json.load(response)["result"]["tools"]
    params = {p for tool in tools for p in tool.get("inputSchema", {}).get("properties", {})}
    return {tool["name"] for tool in tools}, params


def main() -> int:
    config = json.loads((PLUGIN_ROOT / "mcp.json").read_text())["mcpServers"]
    server = config[READ_ONLY_SERVER]
    allowlist = [t.strip() for t in server["headers"]["X-MCP-Tools"].split(",") if t.strip()]
    available, parameters = live_tools(server["url"])
    errors = []

    urls = [c["url"] for c in config.values()]
    if len(urls) != len(set(urls)):
        errors.append(f"connections share a URL, so clients will drop one of them: {urls}")

    reviewed = json.loads((PLUGIN_ROOT / "scripts" / "reviewed_tools.json").read_text())
    reviewed_read_only = set(reviewed["read_only"])
    if set(allowlist) != reviewed_read_only:
        errors.append(
            "X-MCP-Tools does not match reviewed read_only: "
            f"extra={sorted(set(allowlist) - reviewed_read_only)} "
            f"missing={sorted(reviewed_read_only - set(allowlist))}"
        )
    unreviewed = sorted(available - reviewed_read_only - set(reviewed["excluded"]))
    if unreviewed:
        errors.append(f"new server tools to classify in reviewed_tools.json: {unreviewed}")

    unknown = sorted(set(allowlist) - available)
    if unknown:
        errors.append(f"allowlisted tools missing on the server: {unknown}")
    if len(allowlist) != len(set(allowlist)):
        errors.append("allowlist has duplicate names")
    forbidden = sorted(t for t in allowlist if any(re.search(p, t) for p in FORBIDDEN_PATTERNS))
    if forbidden:
        errors.append(f"allowlist contains state-changing or credential tools: {forbidden}")

    cited = set()
    for skill in (PLUGIN_ROOT / "skills").glob("*/SKILL.md"):
        for name in re.findall(r"`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`", skill.read_text()):
            cited.add((name, skill.parent.name))
    known = available | parameters | NON_TOOL_WORDS
    missing = sorted({f"{name} ({skill})" for name, skill in cited if name not in known})
    if missing:
        errors.append(f"skills mention tools or parameters that are not on the server: {missing}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    cited_tools = {n for n, _ in cited if n in available}
    print(f"OK: {len(allowlist)} read-only tools, {len(cited_tools)} tools cited by skills, "
          f"{len(available)} tools on the server.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
