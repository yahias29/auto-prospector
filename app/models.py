# app/models.py
from pydantic import BaseModel, Field
from typing import Optional

class LeadInput(BaseModel):
    profile_url: str = Field(..., description="The LinkedIn profile URL of the lead.")
    # Add any other fields you scrape from Phantombuster
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None

class LeadOutput(LeadInput):
    # This model inherits all fields from LeadInput
    enriched_data: dict = Field(..., description="Data gathered by the research agent.")
    personalized_message: str = Field(..., description="The personalized message drafted by the writer agent.")
    is_new_lead: bool = Field(..., description="Indicates if the lead was new or already in the database.")