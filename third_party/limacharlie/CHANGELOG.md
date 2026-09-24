# Changelog

All notable changes to this plugin will be documented here.

## 1.0.0 — initial release

- Added two MCP connections to LimaCharlie's hosted Streamable HTTP server:
  - `limacharlie` (`https://mcp.limacharlie.io/mcp`), restricted to 185 reviewed read-only tools through the `X-MCP-Tools` header. The server enforces the list on every call. Reads that return credentials, fetch URLs or write files stay off it.
  - `limacharlie-actions` (`https://mcp.limacharlie.io/mcp/all`), with full access, used only after the user approves a specific change. Teams can block it in their MCP policy to stay read-only.
- Auth is OAuth 2.1 with PKCE and dynamic client registration, signing in with Google or Microsoft. The plugin ships no client ID, secret or variables.
- Added six skills:
  - `limacharlie`: connections, org selection, the approval rule, routines, credentials and troubleshooting.
  - `limacharlie-hunt`, `limacharlie-triage`, `limacharlie-detection-engineering`, `limacharlie-endpoint-response` and `limacharlie-config-as-code`.
- Added `scripts/check_mcp_tools.py` and `scripts/reviewed_tools.json`. Together they check the read-only list against a reviewed classification of every server tool, flag new tools that have not been classified, and check every tool the skills mention against the live server.
- Available in Grok Bot and Cursor.
- Logo: LimaCharlie's official mark.
