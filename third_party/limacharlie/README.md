# LimaCharlie

Grok Bot and Cursor plugin that connects agents to [LimaCharlie](https://limacharlie.io), the SecOps platform for EDR telemetry, detection and response, through LimaCharlie's hosted [Model Context Protocol](https://modelcontextprotocol.io/) server at `https://mcp.limacharlie.io/mcp`.

Hunt threats across telemetry, triage detections and cases, build and test detection rules, and investigate or contain endpoints. The plugin is read-only by default, and every change needs your approval.

## Who can use it

- A LimaCharlie account with access to at least one organization. [Sign up](https://app.limacharlie.io) if you don't have one.
- Grok Bot or Cursor.

## Install

1. Open **Plugins** (Grok Bot) or the **Marketplace** (Cursor).
2. Search for **LimaCharlie**.
3. Click **Install**, then connect both LimaCharlie connections when prompted.

## Connections

The plugin adds two connections to the same MCP server, each at its own address:

| Connection | Address | Access |
| --- | --- | --- |
| `limacharlie` | `https://mcp.limacharlie.io/mcp` | **Read-only.** The plugin sends the server a fixed list of 176 read-only tools in the `X-MCP-Tools` header. The server lists only those tools and refuses a call to any other tool on this connection. |
| `limacharlie-actions` | `https://mcp.limacharlie.io/mcp/all` | **Full access**: isolation, sensor tasking, rule deployment, configuration changes and credential reads. The skills use it only after you approve the specific action. |

To keep a team read-only, block `limacharlie-actions` in your team's MCP policy. The skills then describe changes for a person to make in the LimaCharlie web app instead of making them.

## Connecting

Authentication is OAuth. There is no API key or token to paste.

1. Click **Connect** on each LimaCharlie connection.
2. Sign in to LimaCharlie in the browser, with Google or Microsoft.
3. The connection completes on its own. The access token stays with the connector, and the agent never sees it.

The agent acts with **your** LimaCharlie permissions, in every organization you can access. For a narrower scope, sign in as a LimaCharlie user with fewer permissions. For investigation from historical data, grant `sensor.list`, `sensor.get`, `insight.evt.get`, `insight.det.get`, `insight.stat`, `dr.list`, `fp.ctrl`, `yara.get`, `lookup.get` and `audit.get`. Live evidence collection (process lists and similar) also needs `sensor.task`. That permission also allows killing processes and deleting files through `limacharlie-actions`, so grant it only to users who may respond. See [Permission requirements](https://docs.limacharlie.io/6-developer-guide/mcp-server/#permission-requirements).

## What agents can do

| Category | Capabilities | Connection |
| --- | --- | --- |
| Hunting | LCQL queries with validation and cost estimates, IOC sweeps, host timelines, process trees | read-only |
| Triage | Detections, rules, MITRE mapping, detection summaries, cases | read-only |
| Live evidence | Processes, connections, autoruns, services, drivers, files, registry on online hosts | read-only |
| Detection engineering | Draft, validate and unit-test D&R and false-positive rules | read-only |
| Changes | Replay rules against history, deploy/enable/disable rules, isolate/rejoin hosts, sensor tasks, YARA scans, tags, case updates | actions, after approval |
| Config as code | `limacharlie sync` pull, dry-run and push (needs the optional CLI) | CLI, push after approval |

## Approval

Every change is confirmed with you first. Before a change, the agent shows an **Approve / Cancel** prompt that names the action, the organization and the exact targets (sensor IDs and hostnames, rule names, case numbers). Nothing happens until you approve, and each change needs its own approval. Approvals never carry over from earlier messages, sessions or routine definitions.

Routines only read and report. When a routine finds something that needs action, it asks and waits. For containment that must happen with nobody present, the skills propose a LimaCharlie D&R rule with a response action, which you approve and the platform then runs.

## Skills

| Skill | Purpose |
| --- | --- |
| `limacharlie` | Connections, org selection, the approval rule, routines, credentials, troubleshooting |
| `limacharlie-hunt` | LCQL, IOC sweeps, timelines |
| `limacharlie-triage` | Detection triage and cases |
| `limacharlie-detection-engineering` | D&R and false-positive rules: validate, test, replay, deploy |
| `limacharlie-endpoint-response` | Live investigation, isolation, sensor tasking, offline hosts |
| `limacharlie-config-as-code` | Org configuration as code with the limacharlie CLI |

## Security notes

- Telemetry, detections and case content can contain text an attacker wrote. The skills treat it as data and never as instructions or approvals.
- The agent never asks for, prints or stores API keys, JWTs, installation keys or secret values. Some reads are not on the read-only connection, because they return credentials, fetch URLs or write files: secrets, installation keys, outputs, org values, adapter and extension configs, YARA sources, payload downloads, ARL resolution, and AI chat and session histories.
- Content stored in LimaCharlie (SOPs, notes, AI skills, playbooks) is treated as information, never as an approval or an instruction to widen scope.
- The limacharlie CLI has no read-only mode, so the skills treat every CLI command except help and credential-free `sync pull` as a change needing approval, and routines never use it.
- Files and command-line logins on the Grok Bot computer are shared by every Bot on the account. The optional limacharlie CLI is installed and signed in only with your agreement.
- LCQL queries and rule replays are billed by LimaCharlie. The skills validate and estimate broad queries before running them.

## Network endpoints

| Endpoint | Used for |
| --- | --- |
| `https://mcp.limacharlie.io/mcp`, `https://mcp.limacharlie.io/mcp/all` | MCP server (read-only and actions connections) |
| `https://mcp.limacharlie.io/.well-known/*`, `/authorize`, `/token`, `/register` | OAuth 2.1 discovery, dynamic client registration and token exchange |
| `https://api.limacharlie.io`, `https://jwt.limacharlie.io` | LimaCharlie API, used by the MCP server and the optional CLI |

## Maintaining the read-only list

The two connections must keep separate addresses: Grok Bot and Cursor keep only one connection per URL. `/mcp/all` serves the same full tool set as `/mcp`.

The server rejects the whole `X-MCP-Tools` list if it names a tool the server does not have. `scripts/reviewed_tools.json` classifies every tool on the server as `read_only` or `excluded`. Before every release, run:

```bash
python3 scripts/check_mcp_tools.py
```

It checks that the header matches the reviewed read-only set, fails on any new server tool that has not been classified yet, rejects tool names that look like writes, credential reads or URL fetches, and checks every tool the skills mention. It calls only `tools/list`, which needs no credentials.

## Docs

- LimaCharlie documentation: https://docs.limacharlie.io
- Connecting AI assistants: https://docs.limacharlie.io/6-developer-guide/mcp-server/
- Support: support@limacharlie.io

## License

MIT
