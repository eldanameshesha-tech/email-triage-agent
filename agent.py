from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()

@tool
def create_calendar_event(title: str, date: str, time: str) -> str:
    """Create a calendar event for a meeting. Use when the email is requesting a meeting."""
    return f"Event created: '{title}' on {date} at {time}"

@tool
def draft_reply(to: str, subject: str, body: str) -> str:
    """Draft an email reply. Use when the email needs a response."""
    return f"Draft created to {to} — Subject: {subject}"

import requests

@tool
def get_joke() -> str:
    """Fetch a random joke. Use when the email is casual/non-actionable and you want to lighten the response."""
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    data = response.json()
    return f"{data['setup']} — {data['punchline']}"

agent = create_agent(
    model="groq:openai/gpt-oss-120b",
        tools=[create_calendar_event, draft_reply, get_joke],
        system_prompt="""You are an email triage assistant. Given an email's subject and body,
    decide the appropriate action: if it's a meeting request, create a calendar event;
    if it needs a reply, draft a response; if it's casual/non-actionable, use the get_joke
    tool to lighten the response. Always use one of the tools available — never respond
    with plain text only."""
)

test_email = """
Subject: Just saying hi
Body: No action needed, just wanted to say hi and hope you're having a good week!
"""

result = agent.invoke({
    "messages": [{"role": "user", "content": test_email}]
})

print(result["messages"][-1].content)