import base64
import json
from typing import Any
from pydantic import BaseModel

from google.adk.workflow import Workflow, node, START
from google.adk.events.event import Event
from google.adk.events.request_input import RequestInput
from google.adk.agents.context import Context
from google.adk.agents import LlmAgent

from expense_agent.config import EXPENSE_THRESHOLD_USD, RISK_MODEL

class ExpenseReport(BaseModel):
    amount: float
    submitter: str
    category: str
    description: str
    date: str

class RiskEvaluation(BaseModel):
    is_risky: bool
    risk_factors: list[str]
    summary: str

@node
def extract_expense(node_input: Any) -> Event:
    """Parse the incoming event (plain JSON or Pub/Sub base64) and route it."""
    # Handle both plain JSON and base64 encoded Pub/Sub messages
    if isinstance(node_input, dict) and "data" in node_input:
        data_val = node_input["data"]
        if isinstance(data_val, str):
            try:
                decoded = base64.b64decode(data_val).decode('utf-8')
                expense_dict = json.loads(decoded)
            except Exception:
                expense_dict = json.loads(data_val)
        else:
            expense_dict = data_val
    elif isinstance(node_input, str):
        expense_dict = json.loads(node_input)
    else:
        expense_dict = node_input
        
    expense = ExpenseReport(**expense_dict)
    
    # Apply rule: Route based on amount
    if expense.amount < EXPENSE_THRESHOLD_USD:
        route = "auto_approve"
    else:
        route = "risk_review"
        
    # Emit event with the route and save expense to state
    return Event(
        output=expense.model_dump(), 
        route=route, 
        state={"expense": expense.model_dump()}
    )

# The LLM Agent node for reviewing risk
risk_reviewer = LlmAgent(
    name="risk_reviewer",
    model=RISK_MODEL,
    instruction="""You are an expert expense risk reviewer. 
Analyze the provided expense report for any policy violations, anomalies, or risks.
Respond with a JSON object containing is_risky (boolean), risk_factors (list of strings), and summary (string).""",
    output_schema=RiskEvaluation,
    output_key="risk_evaluation"
)

@node
async def human_review(ctx: Context, node_input: Any):
    """Pause for human review if needed, requesting input via HITL."""
    if not ctx.resume_inputs or "human_approval" not in ctx.resume_inputs:
        # Pause the workflow and request human input
        yield RequestInput(
            interrupt_id="human_approval",
            message=f"Expense >= ${EXPENSE_THRESHOLD_USD} needs review. Risk evaluation: {node_input}. Please 'Approve' or 'Reject'."
        )
        return
    
    # Resume workflow with the human's decision
    decision = ctx.resume_inputs["human_approval"]
    yield Event(output={"decision": decision}, state={"human_decision": decision})

@node
def auto_approve(ctx: Context, node_input: Any) -> Event:
    """Handle the auto-approval path for expenses under the threshold."""
    decision = "Auto-Approved (< $100)"
    return Event(output={"decision": decision}, state={"final_decision": decision})

@node
def record_outcome(ctx: Context, node_input: Any) -> Event:
    """Record the final outcome of the human review."""
    expense = ctx.state.get("expense")
    decision = node_input.get("decision", "Unknown")
    
    final_record = {
        "expense": expense,
        "decision": decision,
        "status": "Recorded"
    }
    return Event(output=final_record, state={"final_decision": decision})

# Wire up the graph workflow
root_agent = Workflow(
    name="ambient_expense_agent",
    description="An ambient agent that processes expense reports via a graph workflow.",
    edges=[
        (START, extract_expense),
        # Routing from extract_expense based on the route value returned
        (extract_expense, auto_approve, "auto_approve"),
        (extract_expense, risk_reviewer, "risk_review"),
        
        # After risk review, it goes to human review
        (risk_reviewer, human_review),
        
        # After human makes a decision, record the outcome
        (human_review, record_outcome)
    ]
)
