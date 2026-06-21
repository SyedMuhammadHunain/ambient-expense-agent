.PHONY: install playground run

install:
	uv sync

playground:
	agents-cli playground

run:
	agents-cli run '{"amount": 150.0, "submitter": "alice@company.com", "category": "software", "description": "IDE License", "date": "2026-06-06"}'

serve:
	uv run python -m expense_agent.fast_api_app
