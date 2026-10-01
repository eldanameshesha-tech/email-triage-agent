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