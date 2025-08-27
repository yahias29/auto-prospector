# app/main.py

import os
import requests
import logging
import sys
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

# --- TEMPORARY TEST ENDPOINT WITH HEAVY LOGGING ---
@app.get("/test-serper")
def test_serper_connection():
    logging.info("--- /test-serper endpoint CALLED ---")
    try:
        logging.info("Attempting to get SERPER_API_KEY from environment...")
        serper_key = os.getenv("SERPER_API_KEY")

        if not serper_key:
            logging.error("SERPER_API_KEY environment variable NOT FOUND.")
            raise HTTPException(status_code=500, detail="SERPER_API_KEY is not set on the server.")
        
        logging.info(f"SERPER_API_KEY found. Length: {len(serper_key)}")

        search_url = "https://google.serper.dev/search"
        logging.info(f"Serper URL set to: {search_url}")

        headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
        payload = {'q': 'What is crewAI?'}
        logging.info("Headers and payload prepared.")

        logging.info("Making POST request to Serper using requests library...")
        response = requests.post(search_url, json=payload, headers=headers, timeout=20)
        logging.info(f"Request completed with status code: {response.status_code}")

        response.raise_for_status()
        logging.info("Request successful (raise_for_status passed).")

        json_response = response.json()
        logging.info("Successfully parsed JSON response from Serper.")
        return json_response

    except requests.exceptions.RequestException as e:
        logging.error(f"!!! A requests.exceptions.RequestException occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Requests Library Error: {str(e)}")
    except Exception as e:
        logging.error(f"!!! An UNEXPECTED Exception occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# --- Your Existing Endpoint ---
@app.post("/process_lead", response_model=LeadOutput)
def process_lead(lead: LeadInput):
    # This check prevents processing empty data
    if not lead.profile_url:
        raise HTTPException(status_code=400, detail="profile_url is required")
        
    # Your existing logic
    result = enrich_lead_with_ai(lead.model_dump())
    return result