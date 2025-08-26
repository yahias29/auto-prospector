# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from .models import LeadInput, LeadOutput
from . import database # Import the database module
from .ai_core import enrich_lead_with_ai
import os

app = FastAPI(
    title="Auto-Prospector AI",
    description="An API for enriching business leads with AI.",
    version="0.1.0"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Startup: Creating database table...")
    database.create_leads_table()
    yield
    print("Shutdown: Cleaning up...")

app = FastAPI(
    title="Auto-Prospector AI",
    description="An API for enriching business leads with AI.",
    version="0.1.0",
    lifespan=lifespan
)

USE_CHROMA = os.getenv("USE_CHROMA", "false").lower() == "true"
if USE_CHROMA:
    from app.chroma_loader import init_chroma
    chroma_client = init_chroma()
else:
    chroma_client = None

@app.get("/health")
def health():
    return {"status": "ok", "chroma": bool(chroma_client)}

@app.get("/")
def read_root():
    """A simple endpoint to confirm the API is running."""
    return {"status": "API is running"}

@app.post("/process_lead", response_model=LeadOutput)
async def process_lead(lead: LeadInput):
    """
    Receives lead data, checks for duplicates, enriches it using AI,
    and returns the processed lead data.
    """
    print(f"Received lead for processing: {lead.profile_url}")

    # 1. Database check for duplicates
    if database.check_if_lead_exists(lead.profile_url):
        print(f"Lead is a duplicate: {lead.profile_url}")
        # You could choose to stop here and return an error,
        # but for this workflow, we'll still return a standard response.
        # We just won't run the AI or save to the DB.
        raise HTTPException(status_code=409, detail="Lead already exists in the database.")


    # Convert the Pydantic model to a dictionary to pass to the AI
    lead_data_dict = lead.model_dump()
    ai_result = enrich_lead_with_ai(lead_data_dict)

    # Combine all data into a single object for output and saving
    output_data = LeadOutput(
        **lead.model_dump(),
        enriched_data=ai_result["enriched_data"],
        personalized_message=ai_result["personalized_message"].raw,
        is_new_lead=True
    )
    # 3. Saving the new lead to the database
    print(f"Saving new lead to database: {lead.profile_url}")
    database.add_lead(output_data.model_dump())

    return output_data