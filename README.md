# 𝗔𝗺𝗯𝗶𝗲𝗻𝘁 𝗘𝘅𝗽𝗲𝗻𝘀𝗲 𝗔𝗴𝗲𝗻𝘁

An intelligent, graph-based AI agent that automates expense report processing. Built using the [Google Agent Development Kit (ADK)](https://adk.dev/), this agent evaluates expenses, redacts PII, guards against prompt injections, and dynamically requests human-in-the-loop (HITL) approval for risky claims.

## 🚀 How It Works

The core logic is structured as an ADK `Workflow` (`expense_agent/agent.py`), processing expenses through a series of specialized nodes:

1. **Extract Expense**: Parses incoming payloads and routes low-value expenses to auto-approval while flagging larger ones for review.
2. **Security Checkpoint**: A defensive layer that scrubs PII (e.g., SSNs, Credit Cards) and detects prompt injection attempts *before* the data reaches the LLM. If injection is detected, it immediately escalates to a human.
3. **Risk Reviewer (LLM)**: An LLM Agent analyzes the sanitized expense report for policy violations, anomalies, or risks, outputting a structured evaluation.
4. **Human Review (HITL)**: If the LLM flags the expense as risky, the workflow pauses, securely awaiting a human operator to `Approve` or `Reject` the claim.
5. **Record Outcome**: Logs the final decision.

## Project Structure

```
ambient-expense-agent/
├── app/         # Core agent code
│   ├── agent.py               # Main agent logic
│   └── app_utils/             # App utilities and helpers
├── tests/                     # Unit, integration, and load tests
├── GEMINI.md                  # AI-assisted development guide
└── pyproject.toml             # Project dependencies
```

> 💡 **Tip:** Use [Gemini CLI](https://github.com/google-gemini/gemini-cli) for AI-assisted development - project context is pre-configured in `GEMINI.md`.

## Requirements

Before you begin, ensure you have:
- **uv**: Python package manager (used for all dependency management in this project) - [Install](https://docs.astral.sh/uv/getting-started/installation/) ([add packages](https://docs.astral.sh/uv/concepts/dependencies/) with `uv add <package>`)
- **agents-cli**: Agents CLI - Install with `uv tool install google-agents-cli`
- **Google Cloud SDK**: For GCP services - [Install](https://cloud.google.com/sdk/docs/install)


## Quick Start

Install `agents-cli` and its skills if not already installed:

```bash
uvx google-agents-cli setup
```

Install required packages:

```bash
agents-cli install
```

Test the agent with a local web server:

```bash
agents-cli playground
```

You can also use features from the [ADK](https://adk.dev/) CLI with `uv run adk`.

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `agents-cli install` | Install dependencies using uv                                                         |
| `agents-cli playground` | Launch local development environment                                                  |
| `agents-cli lint`    | Run code quality checks                                                               |
| `agents-cli eval`    | Evaluate agent behavior (generate, grade, analyze, and more — see `agents-cli eval --help`) |
| `uv run pytest tests/unit tests/integration` | Run unit and integration tests                                                        |

## 🛠️ Project Management

| Command | What It Does |
|---------|--------------|
| `agents-cli scaffold enhance` | Add CI/CD pipelines and Terraform infrastructure |
| `agents-cli infra cicd` | One-command setup of entire CI/CD pipeline + infrastructure |
| `agents-cli scaffold upgrade` | Auto-upgrade to latest version while preserving customizations |

---

## Development

Edit your agent logic in `app/agent.py` and test with `agents-cli playground` - it auto-reloads on save.

## Deployment

```bash
gcloud config set project <your-project-id>
agents-cli deploy
```

To add CI/CD and Terraform, run `agents-cli scaffold enhance`.
To set up your production infrastructure, run `agents-cli infra cicd`.

## Observability

Built-in telemetry exports to Cloud Trace, BigQuery, and Cloud Logging.
