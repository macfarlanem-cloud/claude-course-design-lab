"""
Bonus: Upload the Skill to Anthropic's Skills API instead of pasting it in.

Run:  python bonus_skills_api.py
      (no dry-run for this one; it needs a real key)

In Step 3 we copied SKILL.md into the system prompt ourselves. That is
simple and transparent, and it is a fine way to work. The Claude
Developer Platform also has a built-in way to manage Skills: you upload
the skill folder once, get a skill_id, and reference it in any request.
Claude then reads the Skill inside a managed code-execution container.

Two things are different from Step 3:
  - the Skill lives on Anthropic's side, shared across your workspace
  - the request needs the code_execution tool, because that is the
    sandbox where Skills are loaded

This uses beta features, so the exact names below may change. If the
call fails, check the Skills guide at platform.claude.com/docs.
"""

from anthropic.lib import files_from_dir

from lab_helpers import MODEL, PROJECT_DIR, get_client, print_section

if "--dry-run" in __import__("sys").argv:
    print("This bonus step has no dry run. It needs a real API key.")
    raise SystemExit(0)

client = get_client()

# --- 1. Upload the Skill folder (only needs to happen once) ---------------
# Every run of this block creates a new copy in your workspace. After the
# first run, paste the printed id below to reuse it instead of re-uploading.
EXISTING_SKILL_ID = ""   # for example "skill_01AbC..."

if EXISTING_SKILL_ID:
    skill_id = EXISTING_SKILL_ID
    print_section("Reusing uploaded Skill")
else:
    print_section("Uploading skills/humanizing-course-design")
    skill = client.beta.skills.create(
        display_title="Humanizing Course Design",
        files=files_from_dir(str(PROJECT_DIR / "skills" / "humanizing-course-design")),
    )
    skill_id = skill.id
print("Skill id:", skill_id)

# --- 2. Use it in a request ----------------------------------------------
print_section("Asking Claude, with the uploaded Skill attached")
response = client.beta.messages.create(
    model=MODEL,
    max_tokens=2000,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "skills": [
            {"type": "custom", "skill_id": skill_id, "version": "latest"}
        ]
    },
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
    messages=[
        {
            "role": "user",
            "content": (
                "Using your humanizing course design skill, write a 150-word "
                "welcome note for week one of an asynchronous online "
                "introductory soil science course at a community college. "
                "The learners are working adults, many returning to school "
                "after years away."
            ),
        }
    ],
)

print_section("Claude replied")
for block in response.content:
    if block.type == "text":
        print(block.text)

print_section("Checkpoint")
print("You should see a welcome note in the voice the Skill describes.")
print("Reflection: same Skill, two delivery methods. When would you want the")
print("Skill managed centrally (Skills API) versus kept in your own repo?")
