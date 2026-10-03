from main import agent

test_cases = [
    {"subject": "Quick sync tomorrow?", "sender": "Sarah",
     "body": "Can we meet tomorrow at 2pm to discuss the timeline?",
     "expected_tool": "create_calendar_event"},
    {"subject": "Invoice question", "sender": "Mark",
     "body": "Hi, I was charged twice this month. Can you look into it and reply to me?",
     "expected_tool": "draft_reply"},
    {"subject": "FYI - office closed Friday", "sender": "HR",
     "body": "Just a heads up, the office will be closed this Friday for maintenance.",
     "expected_tool": "summarize_only"},
         {"subject": "Call next Monday?", "sender": "Abel",
     "body": "Let's schedule a call next Monday at 10am to go over the proposal.",
     "expected_tool": "create_calendar_event"},
    {"subject": "Report", "sender": "Sara",
     "body": "Can you send me the quarterly report by Friday? Thanks.",
     "expected_tool": "draft_reply"},
    {"subject": "Weekly newsletter", "sender": "news@example.com",
     "body": "This week: 5 tips for better sleep, a new recipe, and our summer sale ends soon.",
     "expected_tool": "summarize_only"},
    {"subject": "Notes from yesterday", "sender": "Mark",
     "body": "Attaching the notes from yesterday's meeting. No action needed.",
     "expected_tool": "summarize_only"},
    {"subject": "Thanks!", "sender": "Temesgen",
     "body": "Thanks for your help last week, really appreciated.",
     "expected_tool": "summarize_only"},
    {"subject": "Free this week?", "sender": "Liya",
     "body": "Are you free to talk sometime this week? No specific time yet.",
     "expected_tool": "draft_reply"},
]

passed = 0
for case in test_cases:
    text = f"Subject: {case['subject']}\nFrom: {case['sender']}\nBody: {case['body']}"
    result = agent.invoke({"messages": [{"role": "user", "content": text}]})

    tool_used = None
    for msg in result["messages"]:
        if hasattr(msg, "name") and msg.name in ("create_calendar_event", "draft_reply", "summarize_only"):
            tool_used = msg.name

    ok = tool_used == case["expected_tool"]
    passed += ok
    print(f"{'PASS' if ok else 'FAIL'} - expected {case['expected_tool']}, got {tool_used} - \"{case['subject']}\"")

print(f"\n{passed}/{len(test_cases)} passed")