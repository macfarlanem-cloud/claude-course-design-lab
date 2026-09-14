"""
Step 1: One message in, one message out.

Run:  python step_1_hello.py
  or: python step_1_hello.py --dry-run

This is the smallest possible conversation with Claude through the API.
Everything later in the lab is a variation on these five ideas:

  client    the connection to Claude (made once)
  model     which Claude you are talking to
  system    who Claude should be for this conversation (the "job description")
  messages  the conversation so far, oldest first
  response  what Claude sends back
"""

from lab_helpers import MODEL, get_client, print_section, text_of

client = get_client()

# Try changing this and running again. This is the single biggest lever
# you have as an educator: you are describing the colleague you want.
SYSTEM_PROMPT = (
    "You are a thoughtful instructional design partner for a community "
    "college instructor. Be warm, concrete, and brief. Never use em dashes."
)

USER_MESSAGE = (
    "In three sentences, what is one thing a first-week online course "
    "module should always do for learners?"
)

print_section("Sending to Claude")
print("System prompt:", SYSTEM_PROMPT)
print("User message: ", USER_MESSAGE)

response = client.messages.create(
    model=MODEL,
    max_tokens=400,          # the most words Claude may write back (roughly 300 words)
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": USER_MESSAGE},
    ],
)

print_section("Claude replied")
print(text_of(response))

print_section("Checkpoint")
print("You should see a short, warm reply above. If you do, Step 1 is done.")
print("Reflection: change SYSTEM_PROMPT to describe a different kind of")
print("colleague (stricter, funnier, more Socratic) and run this again.")
print("Notice how much the reply changes before you touch anything else.")
