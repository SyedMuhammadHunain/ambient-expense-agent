import os

# Threshold for auto-approving expenses
EXPENSE_THRESHOLD_USD = 100.0

# LLM model used for risk reviews
RISK_MODEL = os.getenv("RISK_MODEL", "gemini-2.5-flash")
