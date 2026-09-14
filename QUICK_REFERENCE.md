# Quick Reference: Course-Design Assistant Lab

One page to keep open while you work.

## Commands

| Do this | Type this |
|---|---|
| Turn on the workspace (Mac/Linux) | `source .venv/bin/activate` |
| Turn on the workspace (Windows) | `.venv\Scripts\Activate.ps1` |
| Install libraries | `pip install -r requirements.txt` |
| Check setup | `python step_0_check.py` |
| Step 1, one message | `python step_1_hello.py` |
| Step 2, with a tool | `python step_2_tool.py` |
| Step 3, first run (Claude should ask about learners) | `python step_3_skill.py` |
| Step 3, full module plan | `python step_3_skill.py --with-learners` |
| Step 5 (optional), unpublished page into Canvas | `python step_5_canvas.py` |
| Bonus, Skills API | `python bonus_skills_api.py` |
| Any step without a key or cost | add `--dry-run` |

## The five words

| Word | Plain meaning |
|---|---|
| client | Your connection to Claude. Made once at the top of each script. |
| model | Which Claude you are talking to. Set once in `lab_helpers.py`. |
| system | The job description for this conversation. Your biggest lever. |
| messages | The conversation so far, oldest first. Each entry has a role (user or assistant) and content. |
| response | What Claude sent back. `response.content` holds the pieces; `response.stop_reason` says why it stopped. |

## The tool-use loop

```
you describe the tool  ->  Claude asks to use it  ->  your code runs it
        ^                                                    |
        |                     Claude answers   <-  you send the result back
```

Three signals to watch for in code:

- `stop_reason == "tool_use"`: Claude is waiting on you.
- a block with `type == "tool_use"`: it has `name`, `input`, and an `id`.
- your reply block: `{"type": "tool_result", "tool_use_id": id, "content": result}`.

Claude never runs anything. Your script does, and only what you wrote.

## A Skill, in one breath

A folder with a `SKILL.md` inside. The file starts with a name and a description (so Claude knows when to use it), then plain instructions for how an expert does the work. Load it into the system prompt (Step 3) or upload it to the Skills API (Bonus).

## Where things live

| Want to change | Open |
|---|---|
| The model | `lab_helpers.py`, the `MODEL` line |
| Who Claude is | `SYSTEM_PROMPT` in any step file |
| The request | `USER_MESSAGE` in any step file |
| The syllabus or learners | `materials/` |
| The teaching philosophy | `skills/humanizing-course-design/SKILL.md` |
| Your API key and Canvas settings | `.env` (never share, never commit) |

## When something goes wrong

| You see | Try |
|---|---|
| `No API key found` | Copy `.env.example` to `.env` and paste the key in. Run `python step_0_check.py`. |
| `ModuleNotFoundError: anthropic` | The workspace is off or libraries are not installed. Activate, then `pip install -r requirements.txt`. |
| `authentication_error` | The key is wrong or was deleted. Make a new one at console.anthropic.com. |
| `rate_limit` or `overloaded` | Wait a minute and run again. |
| Claude does not use the tool | Make the tool description and the user message clearer about what file to read. |
| Output has no design notes | Confirm the Skill loaded: the console prints its character count. Check the `<skill>` tags are intact. |
| `Canvas said no (401)` | The Canvas token is wrong or expired. Make a new one under Account, then Settings. |
| `Canvas said no (404)` | Check `CANVAS_BASE_URL` and `CANVAS_COURSE_ID`; you must have a teacher or designer role in that course. |
