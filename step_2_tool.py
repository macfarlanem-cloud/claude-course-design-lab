"""
Step 2: Give Claude a tool (reading a file on your computer).

Run:  python step_2_tool.py
  or: python step_2_tool.py --dry-run

In Step 1, Claude only knew what was in the message. Now we give it a
tool: a small function on your computer that it can ask to run. Claude
cannot run anything by itself. The loop goes like this:

  1. You describe the tool to Claude (name, what it does, what it needs).
  2. Claude reads your request and decides it needs the tool.
     It replies with a "tool_use" block: "please run read_file on X".
  3. YOUR script runs the function and sends the result back.
  4. Claude reads the result and writes its real answer.

Watch the console: you will see each of those moments printed.
"""

import json

from lab_helpers import MODEL, get_client, print_section, read_project_file, text_of

client = get_client()

# --- 1. Describe the tool -------------------------------------------------
# This is a description, not code. Claude reads it the way a new colleague
# would read a note that says "the syllabus is in the shared drive, ask me
# and I will pull it." The clearer the description, the better Claude uses it.
TOOLS = [
    {
        "name": "read_file",
        "description": (
            "Read a text file from the instructor's project folder and return "
            "its full contents. Use this whenever you need to see a syllabus, "
            "a learner profile, or any other course document before answering."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "relative_path": {
                    "type": "string",
                    "description": "Path to the file, relative to the project folder. "
                                   "Example: materials/sample_syllabus.md",
                }
            },
            "required": ["relative_path"],
        },
    }
]

# This is what actually runs when Claude asks. One tool name, one function.
TOOL_FUNCTIONS = {
    "read_file": read_project_file,
}

SYSTEM_PROMPT = (
    "You are an instructional design partner for a community college "
    "instructor. When a question depends on a course document, read the "
    "document with your tool before answering. Never use em dashes."
)

USER_MESSAGE = (
    "Please read materials/sample_syllabus.md and tell me, in five bullet "
    "points, what the course is, who it seems to be for, and one thing you "
    "would want to know about the learners before redesigning a week of it."
)

messages = [{"role": "user", "content": USER_MESSAGE}]

print_section("Sending to Claude, with a tool available")
print("User message:", USER_MESSAGE)

# --- 2 through 4. The tool-use loop --------------------------------------
# We keep calling Claude until it stops asking for tools.
while True:
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages,
    )

    # Whatever Claude said (text, tool requests, or both) goes into the
    # conversation history, so Claude remembers it on the next turn.
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason != "tool_use":
        break  # Claude is finished and has given its real answer.

    # Claude asked for one or more tools. Run each one and collect results.
    tool_results = []
    for block in response.content:
        if block.type != "tool_use":
            continue
        print_section(f"Claude asked to run: {block.name}")
        print("With input:", json.dumps(block.input))

        function_to_run = TOOL_FUNCTIONS[block.name]
        result = function_to_run(**block.input)
        print(f"Your script ran it and got {len(result)} characters back.")

        tool_results.append(
            {
                "type": "tool_result",
                "tool_use_id": block.id,   # ties this result to that request
                "content": result,
            }
        )

    # Tool results go back to Claude as the next "user" turn.
    messages.append({"role": "user", "content": tool_results})

print_section("Claude replied")
print(text_of(response))

print_section("Checkpoint")
print("You should have seen 'Claude asked to run: read_file' above, followed")
print("by an answer that clearly knows what is in the syllabus.")
print("Reflection: Claude never touched your files. Your script did, and only")
print("inside this folder. That boundary is the whole point of tool use.")
