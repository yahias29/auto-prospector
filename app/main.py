# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from .models import LeadInput, LeadOutput
from . import database
import os

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
    # Import only when enabled, and after app is created
    from app.chroma_loader import init_chroma
    chroma_client = init_chroma()
else:
    chroma_client = None

@app.get("/")
def read_root():
    return {"status": "API is running", "chroma": bool(chroma_client)}

@app.post("/process_lead", response_model=LeadOutput)
async def process_lead(lead: LeadInput):
    # Lazy import to avoid pulling chromadb/crewai at module import time
    from .ai_core import enrich_lead_with_ai

    print(f"Received lead for processing: {lead.profile_url}")

    if database.check_if_lead_exists(lead.profile_url):
        print(f"Lead is a duplicate: {lead.profile_url}")
        raise HTTPException(status_code=409, detail="Lead already exists in the database.")

    lead_data_dict = lead.model_dump()
    ai_result = enrich_lead_with_ai(lead_data_dict)

    output_data = LeadOutput(
        **lead.model_dump(),
        enriched_data=ai_result["enriched_data"],
        personalized_message=ai_result["personalized_message"].raw,
        is_new_lead=True
    )

    print(f"Saving new lead to database: {lead.profile_url}")
    database.add_lead(output_data.model_dump())
    return output_data
