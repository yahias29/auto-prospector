# app/ai_core.py
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import AzureChatOpenAI
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# Load environment variables from .env file
load_dotenv()

# --- LLM Configuration ---
# Create an instance of the Azure OpenAI LLM
# This will automatically use environment variables for keys, endpoint, etc.
azure_llm = AzureChatOpenAI(
    openai_api_version=os.environ.get("AZURE_API_VERSION"),
    azure_deployment=os.environ.get("AZURE_DEPLOYMENT_NAME"),
)

# --- Tool Configuration ---
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

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
    tools=[search_tool, scrape_tool],
    verbose=True,
    allow_delegation=False,
    llm=azure_llm,  # Pass the Azure LLM to the agent
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
    llm=azure_llm,  # Pass the Azure LLM to the agent
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
    llm=azure_llm,  # Pass the Azure LLM to the agent
)

# 2. Define the Tasks
# --------------------
# Note: The input variables like {first_name} will be passed in when we run the crew.

research_task = Task(
    description=(
        "1. Use the website scraping tool to read the content of the LinkedIn profile URL: {profile_url}. "
        "2. From the scraped content, identify the person's full name, current company, and professional title. "
        "3. Use the search tool to find recent news or articles about this specific person and their company. "
        "4. Summarize their key accomplishments, career moves, and any recent, noteworthy projects."
    ),
    expected_output=(
        "A concise, 3-4 bullet point summary of the most significant and recent findings about the person, based *only* on the information from their specific LinkedIn profile and related news."
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

def enrich_lead_with_ai(lead_input: dict) -> dict:
    """
    Takes lead input data, runs the AI crew, and returns the enriched data.
    """
    print("🤖 Kicking off AI Crew...")

    # The crew.kickoff() method requires a dictionary of inputs.
    # These keys must match the placeholders in your task descriptions.
    crew_inputs = {
        'profile_url': lead_input.get('profile_url'),
        'first_name': lead_input.get('first_name'),
        'last_name': lead_input.get('last_name'),
        'title': lead_input.get('title'),
        'company': lead_input.get('company')
    }

    # Run the crew and get the final output
    result = crew.kickoff(inputs=crew_inputs)

    # The `crew.kickoff()` result is the output of the LAST task in the sequence.
    enriched_data = {
        "raw_ai_output": result,
        "structured_summary": "Placeholder for structured data from AI." 
    }

    return {
        "enriched_data": enriched_data,
        "personalized_message": result
    }


# --- Optional: A small test block ---
if __name__ == '__main__':
    print("--- Running AI Core Test ---")
    test_lead = {
        "profile_url": "https://www.linkedin.com/in/satyanadella/",
        "first_name": "Satya",
        "company": "Microsoft"
    }
    enriched_result = enrich_lead_with_ai(test_lead)
    print("\n--- AI Crew Finished ---")
    print("\nPersonalized Message:")
    print(enriched_result['personalized_message'])
    print("\nEnriched Data:")
    print(enriched_result['enriched_data'])