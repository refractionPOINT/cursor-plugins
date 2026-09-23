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

The plugin adds two connections to the same MCP server:

| Connection | Access |
| --- | --- |
| `limacharlie` | **Read-only.** The plugin sends the server a fixed list of 191 read-only tools in the `X-MCP-Tools` header. The server lists only those tools and refuses a call to any other tool on this connection. |
| `limacharlie-actions` | **Full access**: isolation, sensor tasking, rule deployment, configuration changes and credential reads. The skills use it only after you approve the specific action. |

To keep a team read-only, block `limacharlie-actions` in your team's MCP policy. The skills then describe changes for a person to make in the LimaCharlie web app instead of making them.

## Connecting

Authentication is OAuth. There is no API key or token to paste.

1. Click **Connect** on each LimaCharlie connection.
2. Sign in to LimaCharlie in the browser, with Google or Microsoft.
3. The connection completes on its own. The access token stays with the connector, and the agent never sees it.

The agent acts with **your** LimaCharlie permissions, in every organization you can access. For a narrower scope, sign in as a LimaCharlie user with fewer permissions. For investigation only, grant `sensor.list`, `sensor.get`, `insight.evt.get`, `insight.det.get`, `insight.stat`, `dr.list` and `audit.get`. See [Permission requirements](https://docs.limacharlie.io/6-developer-guide/mcp-server/#permission-requirements).

## What agents can do

| Category | Capabilities | Connection |
| --- | --- | --- |
| Hunting | LCQL queries with validation and cost estimates, IOC sweeps, host timelines, process trees | read-only |
| Triage | Detections, rules, MITRE mapping, detection summaries, cases | read-only |
| Live evidence | Processes, connections, autoruns, services, drivers, files, registry, YARA scans on online hosts | read-only |
| Detection engineering | Draft, validate and unit-test D&R and false-positive rules | read-only |
| Changes | Replay rules against history, deploy/enable/disable rules, isolate/rejoin hosts, sensor tasks, tags, case updates | actions, after approval |
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
- The agent never asks for, prints or stores API keys, JWTs, installation keys or secret values. Credential-bearing reads (secrets, installation keys, outputs, org values, adapter and extension configs) are not on the read-only connection.
- Files and command-line logins on the Grok Bot computer are shared by every Bot on the account. The optional limacharlie CLI is installed and signed in only with your agreement.
- LCQL queries and rule replays are billed by LimaCharlie. The skills validate and estimate broad queries before running them.

## Network endpoints

| Endpoint | Used for |
| --- | --- |
| `https://mcp.limacharlie.io/mcp` | MCP server (both connections) |
| `https://mcp.limacharlie.io/.well-known/*`, `/authorize`, `/token`, `/register` | OAuth 2.1 discovery, dynamic client registration and token exchange |
| `https://api.limacharlie.io`, `https://jwt.limacharlie.io` | LimaCharlie API, used by the MCP server and the optional CLI |

## Maintaining the read-only list

The server rejects the whole `X-MCP-Tools` list if it names a tool the server does not have. Before every release, run:

```bash
python3 scripts/check_mcp_tools.py
```

It checks the list against the live server, rejects state-changing or credential tools, and checks every tool the skills mention. It calls only `tools/list`, which needs no credentials.

## Docs

- LimaCharlie documentation: https://docs.limacharlie.io
- Connecting AI assistants: https://docs.limacharlie.io/6-developer-guide/mcp-server/
- Support: support@limacharlie.io

## License

MIT
