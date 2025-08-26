# app/ai_core.py
import os

def enrich_lead_with_ai(lead_input: dict) -> dict:
    # Load env when needed
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    os.environ.setdefault("OPENAI_MODEL_NAME", "azure/gpt-5-chat")

    # Deferred imports to avoid startup-time failures
    from crewai import Agent, Task, Crew, Process
    from crewai_tools import SerperDevTool, ScrapeWebsiteTool

    # Optional: only enable chroma if flag true AND platform supports it
    use_chroma = os.getenv("USE_CHROMA", "false").lower() == "true"
    chroma_client = None
    if use_chroma:
        try:
            from app.chroma_loader import init_chroma  # this defaults to duckdb+parquet
            chroma_client = init_chroma()
        except Exception:
            chroma_client = None  # proceed without chroma

    search_tool = SerperDevTool()
    scrape_tool = ScrapeWebsiteTool()

    researcher_agent = Agent(
        role="Senior Business Researcher",
        goal="Find and analyze latest news and background.",
        backstory="Expert researcher synthesizing data quickly.",
        tools=[search_tool, scrape_tool],
        verbose=True,
        allow_delegation=False,
    )
    analyst_agent = Agent(
        role="Lead Qualification Analyst",
        goal="Identify key insights and hooks.",
        backstory="Understands B2B sales and compelling angles.",
        verbose=True,
        allow_delegation=False,
    )
    writer_agent = Agent(
        role="Expert Cold Email Copywriter",
        goal="Draft a concise, personalized email.",
        backstory="Writes emails that get replies.",
        verbose=True,
        allow_delegation=False,
    )

    research_task = Task(
        description=(
            "1. Scrape LinkedIn: {profile_url}. "
            "2. Extract name, company, title. "
            "3. Search recent news about the person/company. "
            "4. Summarize notable accomplishments and projects."
        ),
        expected_output="3-4 bullets with the most significant recent findings.",
        agent=researcher_agent,
    )
    analysis_task = Task(
        description="Identify 2-3 key insights/hooks from the research.",
        expected_output="One short paragraph plus 2-3 bullet talking points.",
        agent=analyst_agent,
    )
    writing_task = Task(
        description=(
            "Write a <150-word personalized email to {first_name}, mention hook first, "
            "end with a low-friction CTA; no subject or sign-off."
        ),
        expected_output="Final email body text.",
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
