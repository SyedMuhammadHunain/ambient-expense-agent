import json
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai.types import Content, Part
from google.adk.events.request_input import RequestInput
from expense_agent.agent import root_agent
from dotenv import load_dotenv

load_dotenv()

async def generate():
    with open("tests/eval/datasets/basic-dataset.json") as f:
        dataset = json.load(f)
        
    traces = {"eval_cases": []}
    runner = InMemoryRunner(agent=root_agent, app_name="expense_agent")
    
    for case in dataset["eval_cases"]:
        case_id = case["eval_case_id"]
        expense = case["expense"]
        expense_str = json.dumps(expense)
        
        await runner.session_service.create_session(session_id=case_id, user_id="eval", app_name="expense_agent")
        
        events_list = [{"author": "user", "content": {"parts": [{"text": expense_str}]}}]
        
        interrupted = False
        
        new_msg = Content(role="user", parts=[Part.from_text(text=expense_str)])
        async for event in runner.run_async(user_id="eval", session_id=case_id, new_message=new_msg):
            if isinstance(event, RequestInput):
                interrupted = True
                break
            if hasattr(event, "output") and event.output:
                events_list.append({
                    "author": "system",
                    "content": {"parts": [{"text": json.dumps(event.output)}]}
                })
                
        if interrupted:
            desc = expense.get("description", "").lower()
            if "bypass" in desc or "ignore" in desc:
                decision = "Reject (Injection Detected)"
            else:
                decision = "Approve (Clean)"
                
            resume_data = {"human_approval": {"decision": decision}}
            resume_msg = Content(role="user", parts=[Part.from_text(text=json.dumps(resume_data))])
            
            async for event in runner.run_async(user_id="eval", session_id=case_id, new_message=resume_msg):
                if hasattr(event, "output") and event.output:
                    events_list.append({
                        "author": "system",
                        "content": {"parts": [{"text": json.dumps(event.output)}]}
                    })
                    
        # Make the last event appear as from the 'ambient_expense_agent'
        if len(events_list) > 1:
            last_event = events_list[-1]
            events_list[-1] = {
                "author": "ambient_expense_agent",
                "content": {
                    "role": "model",
                    "parts": last_event["content"]["parts"]
                }
            }
                    
        trace_case = {
            "eval_case_id": case_id,
            "prompt": {
                "role": "user",
                "parts": [{"text": expense_str}]
            },
            "responses": [
                {
                    "response": events_list[-1]["content"]
                }
            ],
            "agent_data": {
                "agents": {
                    "ambient_expense_agent": {
                        "agent_id": "ambient_expense_agent",
                        "instruction": "Expense approval agent"
                    }
                },
                "turns": [
                    {
                        "turn_index": 0,
                        "events": events_list
                    }
                ]
            }
        }
        traces["eval_cases"].append(trace_case)
        
    with open("artifacts/traces/generated_traces.json", "w") as f:
        json.dump(traces, f, indent=2)
        
    print("Generated traces in artifacts/traces/generated_traces.json")

if __name__ == "__main__":
    asyncio.run(generate())
