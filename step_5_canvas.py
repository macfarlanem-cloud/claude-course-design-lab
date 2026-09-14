"""
Step 5 (optional): Publish the module into Canvas with a second tool.

Run:  python step_5_canvas.py --dry-run     (safe: prints what would be sent)
      python step_5_canvas.py               (creates an UNPUBLISHED page in Canvas)

Step 3 left a module plan in output/week6_module_plan.md. Now Claude gets
two tools instead of one:

  read_file           the same tool as before, to read that plan
  create_canvas_page  a new tool that creates a page in one of your Canvas
                      courses through the Canvas API

Claude reads the plan, turns it into clean Canvas HTML, and asks your
script to create the page. Your script talks to Canvas. Claude never
holds your Canvas token; only your script does.

The page is created unpublished, so nothing reaches learners until you
open it in Canvas, check it, and publish it yourself.

You need three lines in .env (see .env.example):
  CANVAS_BASE_URL    for example https://yourcollege.instructure.com
  CANVAS_TOKEN       Canvas > Account > Settings > New Access Token
  CANVAS_COURSE_ID   the number in the course URL, /courses/123456
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

from lab_helpers import (
    MODEL, PROJECT_DIR, dry_run_requested, get_client, print_section,
    read_project_file, text_of,
)

client = get_client()

# --- The Canvas tool's function -------------------------------------------
def create_canvas_page(title: str, html_body: str) -> str:
    """Create an unpublished page in the Canvas course named in .env."""
    base_url = os.environ.get("CANVAS_BASE_URL", "").rstrip("/")
    token = os.environ.get("CANVAS_TOKEN", "")
    course_id = os.environ.get("CANVAS_COURSE_ID", "")

    if dry_run_requested():
        return (f"DRY RUN. Would create an unpublished page titled '{title}' "
                f"({len(html_body)} characters of HTML) in course {course_id or '?'} "
                f"at {base_url or '?'}.")

    if not (base_url and token and course_id):
        return ("Missing CANVAS_BASE_URL, CANVAS_TOKEN, or CANVAS_COURSE_ID in .env. "
                "Add them and run again.")

    # The Canvas API expects form-encoded fields named wiki_page[...].
    data = urllib.parse.urlencode({
        "wiki_page[title]": title,
        "wiki_page[body]": html_body,
        "wiki_page[published]": "false",
    }).encode()
    request = urllib.request.Request(
        f"{base_url}/api/v1/courses/{course_id}/pages",
        data=data,
        method="POST",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as reply:
            page = json.loads(reply.read())
    except urllib.error.HTTPError as error:
        return f"Canvas said no ({error.code}): {error.read().decode()[:300]}"
    return (f"Created unpublished page '{page['title']}'. "
            f"Open it at {base_url}/courses/{course_id}/pages/{page['url']}")


# --- Two tools ------------------------------------------------------------
TOOLS = [
    {
        "name": "read_file",
        "description": "Read a text file from the instructor's project folder "
                       "and return its full contents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "relative_path": {"type": "string",
                                  "description": "Path relative to the project folder"}
            },
            "required": ["relative_path"],
        },
    },
    {
        "name": "create_canvas_page",
        "description": (
            "Create a new, unpublished content page in the instructor's Canvas "
            "course. Use it once, after you have the final HTML ready. Returns "
            "a link to the page or an error message."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Page title as learners will see it"},
                "html_body": {"type": "string",
                              "description": "The page body as clean HTML (h2, h3, p, ul, "
                                             "ol, strong, table). No <html> or <body> tags."},
            },
            "required": ["title", "html_body"],
        },
    },
]
TOOL_FUNCTIONS = {
    "read_file": read_project_file,
    "create_canvas_page": create_canvas_page,
}

SYSTEM_PROMPT = (
    "You are an instructional design partner for a community college "
    "instructor. You have a tool to read files and a tool to create a Canvas "
    "page. Convert markdown to clean, accessible HTML: real headings in order, "
    "short paragraphs, lists for lists, a table for the rubric, descriptive link "
    "text. Keep the instructor's wording. Leave out any 'design notes' section, "
    "which is for the instructor, not learners. Never use em dashes."
)

USER_MESSAGE = (
    "Read output/week6_module_plan.md and create it as a Canvas page titled "
    "with the week and topic from the plan. Then tell me the link."
)

plan_path = PROJECT_DIR / "output" / "week6_module_plan.md"
if not plan_path.is_file() and not dry_run_requested():
    print("No module plan found. Run 'python step_3_skill.py --with-learners' first.")
    sys.exit(1)

messages = [{"role": "user", "content": USER_MESSAGE}]
print_section("Sending to Claude, with two tools available")

while True:
    response = client.messages.create(
        model=MODEL, max_tokens=6000, system=SYSTEM_PROMPT,
        tools=TOOLS, messages=messages,
    )
    messages.append({"role": "assistant", "content": response.content})
    if response.stop_reason != "tool_use":
        break
    tool_results = []
    for block in response.content:
        if block.type != "tool_use":
            continue
        print_section(f"Claude asked to run: {block.name}")
        shown = {k: (v[:80] + "...") if isinstance(v, str) and len(v) > 80 else v
                 for k, v in block.input.items()}
        print("With input:", json.dumps(shown))
        result = TOOL_FUNCTIONS[block.name](**block.input)
        print("Result:", result[:200])
        tool_results.append(
            {"type": "tool_result", "tool_use_id": block.id, "content": result}
        )
    messages.append({"role": "user", "content": tool_results})

print_section("Claude replied")
print(text_of(response))

print_section("Checkpoint")
print("Expected: Claude read the plan, then called create_canvas_page once,")
print("and you have a link to an UNPUBLISHED page. Open it in Canvas, read it")
print("as a learner would, fix anything, and publish only when you are happy.")
print("Reflection: which parts of this would you never hand to a tool without")
print("a human check? The 'published: false' line is where that judgment lives.")
