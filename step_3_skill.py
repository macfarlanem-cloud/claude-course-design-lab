"""
Step 3: Load a Skill so the output follows your teaching philosophy.

Run:  python step_3_skill.py                   (first run: watch what Claude asks)
      python step_3_skill.py --with-learners   (second run: full module plan)
  or add --dry-run to either.

A Skill is a plain-text file (SKILL.md) that tells Claude how an expert
does a kind of work: the order to work in, the frameworks to apply, the
checks to run before finishing. Here we load humanizing-course-design,
a Skill written by an educator, and put it in the system prompt.

Nothing else changes from Step 2. Same tool, same loop. The Skill is
what turns "an assistant that can read files" into "a design partner
that works the way you do."
"""

import json
import sys
from pathlib import Path

from lab_helpers import (
    MODEL, PROJECT_DIR, get_client, load_skill, print_section,
    read_project_file, text_of,
)

client = get_client()

# --- Load the Skill -------------------------------------------------------
SKILL_TEXT = load_skill("humanizing-course-design")

SYSTEM_PROMPT = (
    "You are an instructional design partner for a community college "
    "instructor. Read course documents with your tool before designing. "
    "Follow the Skill below exactly. Never use em dashes.\n\n"
    "<skill>\n" + SKILL_TEXT + "\n</skill>"
)

# --- Same tool as Step 2 --------------------------------------------------
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
                    "description": "Path relative to the project folder, "
                                   "for example materials/sample_syllabus.md",
                }
            },
            "required": ["relative_path"],
        },
    }
]
TOOL_FUNCTIONS = {"read_file": read_project_file}

# --- The request ----------------------------------------------------------
# First run: we deliberately say nothing about who the learners are.
# The Skill says "learners first", so a good design partner should ask.
# Second run (--with-learners): we point Claude at the learner profile.
with_learners = "--with-learners" in sys.argv

USER_MESSAGE = (
    "Read materials/sample_syllabus.md. Redesign Week 6 as a fully "
    "asynchronous online module: a short welcome note, the week's outcomes, "
    "one learning activity, one discussion prompt, and one assignment with "
    "purpose, task, and criteria. Write it ready to paste into Canvas."
)
if with_learners:
    USER_MESSAGE += (
        " Before you design, also read materials/learner_profile.md so you "
        "know who these learners are."
    )

messages = [{"role": "user", "content": USER_MESSAGE}]

print_section("Sending to Claude, with the Skill loaded")
print(f"Skill loaded: humanizing-course-design ({len(SKILL_TEXT)} characters)")
print("Learner profile provided:", "yes" if with_learners else "no (on purpose)")

# --- The tool-use loop, exactly as in Step 2 ------------------------------
while True:
    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=messages,
    )
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason != "tool_use":
        break

    tool_results = []
    for block in response.content:
        if block.type != "tool_use":
            continue
        print_section(f"Claude asked to run: {block.name}")
        print("With input:", json.dumps(block.input))
        result = TOOL_FUNCTIONS[block.name](**block.input)
        tool_results.append(
            {"type": "tool_result", "tool_use_id": block.id, "content": result}
        )
    messages.append({"role": "user", "content": tool_results})

# --- Show the result and save it ------------------------------------------
answer = text_of(response)
print_section("Claude replied")
print(answer)

output_name = "week6_module_plan.md" if with_learners else "week6_first_run.md"
output_path = PROJECT_DIR / "output" / output_name
output_path.write_text(answer, encoding="utf-8")
print_section("Saved")
print("Written to:", output_path.relative_to(PROJECT_DIR))

print_section("Checkpoint")
if not with_learners:
    print("Expected on this first run: Claude reads the syllabus and then asks")
    print("you about the learners instead of charging ahead. That is the Skill")
    print("working ('learners first'). Now run:")
    print("    python step_3_skill.py --with-learners")
else:
    print("Expected: a complete Week 6 module that names the learners from the")
    print("profile, states purpose/task/criteria for the assignment, and ends")
    print("with a 'design notes' section naming the frameworks used (UDL, TiLT,")
    print("culturally responsive practice, accessibility). Open the saved file.")
    print("Reflection: search the plan for a decision only a teacher would")
    print("notice is wrong or generic. That is your expertise doing its job.")
