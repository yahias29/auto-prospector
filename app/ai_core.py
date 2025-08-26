# app/ai_core.py
import os

def enrich_lead_with_ai(lead_input: dict) -> dict:
    """
    Takes lead input data, builds the AI crew, runs it, and returns the enriched data.
    All heavy imports and constructions are deferred to avoid startup failures on Azure.
    """
    # Read flags at call time
    use_chroma = os.getenv("USE_CHROMA", "false").lower() == "true"

    # Load env lazily only if needed (optional)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    # Azure OpenAI model selection
    os.environ.setdefault("OPENAI_MODEL_NAME", "azure/gpt-5-chat")

    # Import libraries only when the endpoint is invoked, preventing module-import side effects
    from crewai import Agent, Task, Crew, Process
    from crewai_tools import SerperDevTool, ScrapeWebsiteTool

    # If later enabling chroma on Azure, ensure the code path uses a backend that does not require system sqlite
    # or is completely optional. Do NOT import chromadb here on Azure unless you’ve containerized.
    if use_chroma:
        # Example: only import if really required, and prefer non-sqlite config paths in your chroma_loader
        try:
            from app.chroma_loader import init_chroma
            chroma_client = init_chroma()  # duckdb+parquet by default
        except Exception:
            chroma_client = None
    else:
        chroma_client = None

    # Tools
    search_tool = SerperDevTool()
    scrape_tool = ScrapeWebsiteTool()

    # Agents
    researcher_agent = Agent(
        role="Senior Business Researcher",
        goal="Find and analyze the latest news, projects, and professional background of a person.",
        backstory=(
            "You are an expert researcher with a knack for digging up relevant and up-to-date information "
            "on individuals and their companies. You can quickly synthesize data from various sources."
        ),
        tools=[search_tool, scrape_tool],
        verbose=True,
        allow_delegation=False,
    )

    analyst_agent = Agent(
        role="Lead Qualification Analyst",
        goal="Analyze research findings to identify key insights and potential angles for personalized outreach.",
        backstory=(
            "You are a sharp analyst with a deep understanding of B2B sales and can pinpoint compelling hooks."
        ),
        verbose=True,
        allow_delegation=False,
    )

    writer_agent = Agent(
        role="Expert Cold Email Copywriter",
        goal="Draft a concise, highly personalized email to a lead.",
        backstory=(
            "You craft emails that get replies, referencing specific, relevant details about the recipient."
        ),
        verbose=True,
        allow_delegation=False,
    )

    # Tasks
    research_task = Task(
        description=(
            "1. Use the website scraping tool to read the LinkedIn profile URL: {profile_url}. "
            "2. Identify full name, current company, and professional title from the scraped content. "
            "3. Use the search tool to find recent news or articles about the person and their company. "
            "4. Summarize key accomplishments, career moves, and recent noteworthy projects."
        ),
        expected_output=(
            "3-4 bullet points with the most significant recent findings based only on profile and news."
        ),
        agent=researcher_agent,
    )

    analysis_task = Task(
        description=(
            "From the research summary, identify 2-3 key insights or hooks with the most compelling angle."
        ),
        expected_output=(
            "One short paragraph with the primary angle, plus 2-3 bullet points of talking points."
        ),
        agent=analyst_agent,
    )

    writing_task = Task(
        description=(
            "Using the identified talking points, write a short, personalized email to {first_name} "
            "under 150 words, authentic tone, mention the hook first, and end with a low-friction CTA. "
            "Do NOT include subject line or sign-off."
        ),
        expected_output="The final email body as a single text block.",
        agent=writer_agent,
    )

    crew = Crew(
        agents=[researcher_agent, analyst_agent, writer_agent],
        tasks=[research_task, analysis_task, writing_task],
        process=Process.sequential,
        verbose=True,
    )

    crew_inputs = {
        "profile_url": lead_input.get("profile_url"),
        "first_name": lead_input.get("first_name"),
        "last_name": lead_input.get("last_name"),
        "title": lead_input.get("title"),
        "company": lead_input.get("company"),
    }

    result = crew.kickoff(inputs=crew_inputs)

    enriched_data = {
        "raw_ai_output": result,
        "structured_summary": "Placeholder for structured data from AI.",
    }

    return {
        "enriched_data": enriched_data,
        "personalized_message": result,
        "chroma_enabled": bool(chroma_client),
    }

if __name__ == "__main__":
    # Optional local test
    test_lead = {
        "profile_url": "https://www.linkedin.com/in/someone/",
        "first_name": "Jane",
        "company": "ExampleCo"
    }
    out = enrich_lead_with_ai(test_lead)
    print(out)
