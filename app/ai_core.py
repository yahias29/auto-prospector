# app/ai_core.py
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import AzureChatOpenAI
from crewai_tools import SerperDevTool

# NEW: Add imports for SQLAlchemy database operations
from sqlalchemy import create_engine, text, Table, Column, Integer, String, MetaData

# Load environment variables from .env file
load_dotenv()

# --- Database Setup for Deduplication ---
# NEW: Create the engine with a persistent file path
engine = create_engine("sqlite:///leads.db")
metadata = MetaData()

# NEW: Define the 'leads' table schema
leads_table = Table(
    'leads', metadata,
    Column('id', Integer, primary_key=True),
    Column('profile_url', String, unique=True, nullable=False)
)

# NEW: Function to create the table if it doesn't exist
def create_db_and_tables():
    metadata.create_all(engine)

# NEW: Call the function to ensure the table exists when the app starts
create_db_and_tables()

# NEW: Helper function to check if a lead exists
def lead_exists(profile_url: str) -> bool:
    with engine.connect() as connection:
        query = text("SELECT 1 FROM leads WHERE profile_url = :url")
        result = connection.execute(query, {"url": profile_url}).scalar_one_or_none()
        return result is not None

# NEW: Helper function to add a lead to the database
def add_lead(profile_url: str):
    with engine.connect() as connection:
        query = text("INSERT INTO leads (profile_url) VALUES (:url)")
        connection.execute(query, {"url": profile_url})
        connection.commit()


# --- LLM Configuration ---
azure_llm = AzureChatOpenAI(
    openai_api_version=os.environ.get("OPENAI_API_VERSION"),
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

# --- Tool Configuration ---
search_tool = SerperDevTool()

# 1. Define the Agents
# -------------------
researcher_agent = Agent(
    role='Senior Business Researcher',
    goal='Find and analyze the latest news, projects, and professional background of a person.',
    backstory=(
        "You are an expert researcher with a knack for digging up relevant "
        "and up-to-date information on individuals and their companies. "
        "You are a master of web searches and can quickly synthesize data from various sources."
    ),
    tools=[search_tool],
    verbose=True,
    allow_delegation=False,
    llm=azure_llm,
)

analyst_agent = Agent(
    role='Lead Qualification Analyst',
    goal='Analyze research findings to identify key insights and potential angles for a personalized outreach.',
    backstory=(
        "You are a sharp analyst with a deep understanding of B2B sales. "
        "You can look at a person's professional history and recent company activities "
        "and pinpoint the most compelling reasons for a conversation."
    ),
    verbose=True,
    allow_delegation=False,
    llm=azure_llm,
)

writer_agent = Agent(
    role='Expert Cold Email Copywriter',
    goal='Draft a compelling, concise, and highly personalized email to a lead.',
    backstory=(
        "You are a renowned copywriter, famous for your ability to craft emails that get replies. "
        "You avoid generic templates and focus on creating genuine connections by referencing "
        "specific, relevant details about the recipient."
    ),
    verbose=True,
    allow_delegation=False,
    llm=azure_llm,
)

# 2. Define the Tasks
# --------------------
research_task = Task(
    description=(
        "You have been given the following information about a lead: "
        "Name: {first_name} {last_name}, "
        "Title: {title}, "
        "Company: {company}. "
        "Your task is to use the search tool to find the most recent and relevant news, articles, or projects related to this person and their company. "
        "Focus on their key accomplishments, recent career moves, and any noteworthy company news or projects they might be involved in."
    ),
    expected_output=(
        "A concise, 3-4 bullet point summary of the most significant and recent findings about the person and their company."
    ),
    agent=researcher_agent
)

analysis_task = Task(
    description=(
        "Based on the research summary, identify 2-3 key insights or 'hooks'. "
        "What is the most compelling, recent event or achievement we could mention? "
        "Is it a new project? A company milestone? A recent promotion? "
        "Formulate these as talking points for an email."
    ),
    expected_output=(
        "A short paragraph outlining the primary angle for outreach, followed by 2-3 bullet points "
        "of the specific talking points to be used in the email."
    ),
    agent=analyst_agent
)

writing_task = Task(
    description=(
        "Using the identified talking points, write a short, personalized email to {first_name}. "
        "The email should be under 150 words. "
        "It must sound authentic, not like a template. "
        "Start by mentioning the specific hook/insight. "
        "End with a clear, low-friction call to action."
        "Do NOT include a subject line or sign-off like 'Best regards'."
    ),
    expected_output=(
        "The final, ready-to-send email body as a single block of text."
    ),
    agent=writer_agent
)

# 3. Assemble the Crew
# --------------------
crew = Crew(
    agents=[researcher_agent, analyst_agent, writer_agent],
    tasks=[research_task, analysis_task, writing_task],
    process=Process.sequential,
    verbose=True
)

# 4. Create a function to run the crew
# ------------------------------------

# MODIFIED: This function now includes the deduplication logic
def enrich_lead_with_ai(lead_input: dict) -> dict:
    """
    Takes lead input data, runs the AI crew, and returns the enriched data.
    Includes a deduplication check to avoid processing the same lead twice.
    """
    profile_url = lead_input.get('profile_url')

    # MODIFIED: Check if the lead already exists in the database
    if lead_exists(profile_url):
        print(f" DUPLICATE: Lead with URL {profile_url} has already been processed.")
        # Return a specific message for duplicates
        return {
            "enriched_data": {
                "raw_ai_output": "DUPLICATE",
                "structured_summary": "This lead has already been processed."
            },
            "personalized_message": "This lead is a duplicate and was not processed again."
        }

    print("🤖 Kicking off AI Crew...")

    crew_inputs = {
        'profile_url': profile_url,
        'first_name': lead_input.get('first_name'),
        'last_name': lead_input.get('last_name'),
        'title': lead_input.get('title'),
        'company': lead_input.get('company')
    }

    result = crew.kickoff(inputs=crew_inputs)
    
    # MODIFIED: Add the successfully processed lead to the database
    add_lead(profile_url)
    print(f" SUCCESS: Lead {profile_url} processed and added to the database.")

    enriched_data = {
        "raw_ai_output": result,
        "structured_summary": "Placeholder for structured data from AI."
    }

    return {
        "enriched_data": enriched_data,
        "personalized_message": result
    }