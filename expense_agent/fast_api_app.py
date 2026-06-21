# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import logging

import google.auth
from fastapi import FastAPI, Request
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import InMemoryRunner

from expense_agent.app_utils.telemetry import setup_telemetry
from expense_agent.app_utils.typing import Feedback
from expense_agent.agent import root_agent

setup_telemetry()
_, project_id = google.auth.default()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

# Artifact bucket for ADK (created by Terraform, passed via env var)
logs_bucket_name = os.environ.get("LOGS_BUCKET_NAME")

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# In-memory session configuration - no persistent storage
session_service_uri = None

artifact_service_uri = f"gs://{logs_bucket_name}" if logs_bucket_name else None

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=artifact_service_uri,
    allow_origins=allow_origins,
    session_service_uri=session_service_uri,
    otel_to_cloud=False,
    auto_create_session=True,
)
app.title = "ambient-expense-agent"
app.description = "API for interacting with the Agent ambient-expense-agent"


@app.post("/apps/expense_agent/trigger/pubsub")
async def pubsub_trigger(request: Request):
    """Handle incoming Pub/Sub trigger messages."""
    try:
        envelope = await request.json()
    except Exception:
        return {"status": "error", "message": "Invalid JSON"}

    message = envelope.get("message", {})
    subscription = envelope.get("subscription", "default")
    
    # Normalize subscription path down to a short name to keep session records readable
    short_session_id = subscription.split("/")[-1]
    
    data_b64 = message.get("data", "")
    
    # Decode the base64 payload so the agent receives raw JSON text
    import base64
    try:
        decoded_text = base64.b64decode(data_b64).decode("utf-8")
    except Exception:
        decoded_text = data_b64 # Fallback if not base64
        
    logger.info(f"Received Pub/Sub message from subscription: {short_session_id}")
    
    try:
        import httpx
        
        payload = {
            "appName": "expense_agent",
            "userId": "default",
            "sessionId": short_session_id,
            "newMessage": {
                "role": "user",
                "parts": [{"text": decoded_text}]
            },
            "streaming": False
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post("http://127.0.0.1:8080/run", json=payload)
            response.raise_for_status()
            
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/feedback")
def collect_feedback(feedback: Feedback) -> dict[str, str]:
    """Collect and log feedback.

    Args:
        feedback: The feedback data to log

    Returns:
        Success message
    """
    logger.info(f"Feedback received: {feedback.model_dump()}")
    return {"status": "success"}


# Main execution
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
