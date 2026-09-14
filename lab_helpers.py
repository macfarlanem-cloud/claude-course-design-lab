"""
lab_helpers.py

Small helpers shared by every step of the lab.

You do not need to read this file to complete the lab. It does three things:

1. get_client()      Connects to Claude using the API key in your .env file.
                      If you run a step with --dry-run, it hands back a pretend
                      client instead so you can walk the whole lab with no key
                      and no cost.
2. read_project_file  Reads a file from this project folder (used as a tool).
3. print_section      Prints a labeled divider so console output is easy to follow.

Curious how the pretend client works? It is at the bottom of this file.
"""

import os
import sys
from pathlib import Path

# The model every step uses. Change it here and every step follows.
MODEL = "claude-sonnet-5"

# The folder this file lives in. Every path in the lab is relative to it,
# so the scripts work no matter which folder you run them from.
PROJECT_DIR = Path(__file__).resolve().parent


def dry_run_requested() -> bool:
    """True if the learner passed --dry-run or set DRY_RUN=1."""
    return "--dry-run" in sys.argv or os.environ.get("DRY_RUN") == "1"


def get_client():
    """Return a real Claude client, or a pretend one in dry-run mode."""
    if dry_run_requested():
        print("(dry run: no API call will be made, no key needed)\n")
        return FakeClient()

    # python-dotenv loads ANTHROPIC_API_KEY from the .env file into the
    # environment. The anthropic library reads it from there automatically.
    from dotenv import load_dotenv
    import anthropic

    load_dotenv(PROJECT_DIR / ".env")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("No API key found. Copy .env.example to .env and paste your key in,")
        print("or run this step with --dry-run to walk through it without a key.")
        sys.exit(1)
    return anthropic.Anthropic()


def read_project_file(relative_path: str) -> str:
    """
    Read a text file inside this project folder and return its contents.

    This is the function Claude gets to call in Step 2 and Step 3.
    Two guardrails keep it safe:
      - it only reads files inside the project folder, never outside it
      - it returns a clear message instead of crashing if the file is missing
    """
    target = (PROJECT_DIR / relative_path).resolve()
    if PROJECT_DIR not in target.parents and target != PROJECT_DIR:
        return f"Refused: {relative_path} is outside the project folder."
    if not target.is_file():
        return f"File not found: {relative_path}"
    return target.read_text(encoding="utf-8")


def load_skill(skill_name: str) -> str:
    """Read a SKILL.md file from the skills folder and return its text."""
    return read_project_file(f"skills/{skill_name}/SKILL.md")


def text_of(response) -> str:
    """Join every text block in a Claude response into one string."""
    return "".join(block.text for block in response.content if block.type == "text")


def print_section(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


# ---------------------------------------------------------------------------
# Pretend client for --dry-run. Ignore unless you are curious.
#
# It imitates the two things the real client does in this lab:
#   - answer a plain message with text
#   - when it has tools and has not yet seen a tool result, ask to read the
#     syllabus (so Step 2 and Step 3 show the full tool-use loop)
# ---------------------------------------------------------------------------

class _Block:
    def __init__(self, **fields):
        self.__dict__.update(fields)


class _Response:
    def __init__(self, content, stop_reason):
        self.content = content
        self.stop_reason = stop_reason


_CANNED_INPUTS = {
    "read_file": {"relative_path": "materials/sample_syllabus.md"},
    "create_canvas_page": {
        "title": "Week 6: Cover Crops and Soil Health (dry run)",
        "html_body": "<h2>Welcome to Week 6</h2><p>Placeholder page body.</p>",
    },
}


class _FakeMessages:
    def create(self, **kwargs):
        messages = kwargs.get("messages", [])
        tools = kwargs.get("tools", [])
        # Count how many tool results have come back so far, then ask for
        # the next tool in the list. One tool per turn, each used once.
        results_so_far = sum(
            1 for m in messages
            if isinstance(m.get("content"), list)
            for b in m["content"]
            if isinstance(b, dict) and b.get("type") == "tool_result"
        )
        if results_so_far < len(tools):
            tool = tools[results_so_far]
            return _Response(
                content=[_Block(type="tool_use", id=f"toolu_dryrun_{results_so_far}",
                                name=tool["name"],
                                input=_CANNED_INPUTS.get(tool["name"], {}))],
                stop_reason="tool_use",
            )
        system = kwargs.get("system", "")
        if "create_canvas_page" in str(tools):
            reply = "Dry run: the page would now be in Canvas as an unpublished draft."
        elif "Humanizing Course Design" in system:
            reply = (
                "# Week 6 redesign (dry run)\n\n"
                "This is placeholder text. With a real API key, Claude reads the "
                "syllabus you gave it, applies the Skill, and writes a full module "
                "plan here, ending with a Design notes section.\n\n"
                "## Design notes\n- Humanizing pedagogy/andragogy: (placeholder)\n"
                "- UDL: (placeholder)\n- TiLT: (placeholder)\n"
            )
        else:
            reply = "Hello from the dry-run client. Everything is wired up correctly."
        return _Response(content=[_Block(type="text", text=reply)], stop_reason="end_turn")


class FakeClient:
    def __init__(self):
        self.messages = _FakeMessages()
