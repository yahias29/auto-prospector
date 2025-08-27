# app/main.py

import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# --- Detailed Logging Configuration ---
# This forces all log messages to go to the standard output,
# which is what Azure's Log Stream captures.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout
)

# Load environment variables
load_dotenv()

# Your existing Pydantic models
class LeadInput(BaseModel):
    profile_url: str
    first_name: str | None = None
    last_name: str | None = None
    title: str | None = None
    company: str | None = None

class EnrichedData(BaseModel):
    raw_ai_output: str
    structured_summary: str

class LeadOutput(BaseModel):
    enriched_data: EnrichedData
    personalized_message: str

# Create FastAPI app
app = FastAPI()

# Import your AI core function AFTER configuring logging
from .ai_core import enrich_lead_with_ai

@app.get("/")
def read_root():
    return {"status": "API is running"}

# --- Your Existing Endpoint ---
@app.post("/process_lead", response_model=LeadOutput)
def process_lead(lead: LeadInput):
    # This check prevents processing empty data
    if not lead.profile_url:
        raise HTTPException(status_code=400, detail="profile_url is required")
        
    # Your existing logic
    result = enrich_lead_with_ai(lead.model_dump())
    return result