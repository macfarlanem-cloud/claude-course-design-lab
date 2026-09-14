# Build a Course-Design Assistant with the Claude API

A hands-on lab for educators who are not engineers.

In about 90 minutes you will build a small, real assistant that reads a syllabus from your computer, applies a teaching philosophy you can inspect line by line, and writes a ready-to-paste course module. Along the way you will use the three ideas that everything on the Claude Developer Platform is built from: messages, tools, and Skills. An optional last step publishes the result straight into a Canvas course.

You do not need to know Python. You need to be able to open a terminal, copy commands, and be curious about what happens when you change things.

Want the big picture before the steps? Read [How This Lab Works](HOW_IT_WORKS.md), one page with a diagram of the loop that everything here is built on.

## What you will be able to do

By the end of this lab you will be able to:

1. Send a message to Claude through the API and explain what a system prompt does.
2. Give Claude a tool (a function on your computer) and describe, in your own words, who runs it and why that boundary matters.
3. Load a Skill (a plain-text file that captures how an expert works) and show that it changed Claude's behavior.
4. Swap in your own syllabus, learners, and Skill, so the assistant works the way you teach.

## How the lab is designed

This lab follows the same principles it teaches. Each step has one new idea, a checkpoint you can verify yourself, and a short reflection. Steps build on each other: Step 3 is Step 2 plus one thing. Every script narrates what it is doing in the console, so you can watch the conversation between your computer and Claude rather than take it on faith.

The pedagogical stance underneath it: the quality of what AI produces in a classroom is decided by the expertise of the person directing it, not by their technical fluency. The lab is built so that your judgment as a teacher is the tool that matters most.

## Before you start

You will need:

- A computer with Python 3.10 or newer. Check with `python3 --version` (Mac/Linux) or `python --version` (Windows). If you need Python, download it from python.org.
- An Anthropic API key. Sign in at console.anthropic.com, open API Keys, and create one. New accounts often include free credit; running this whole lab costs well under a dollar.
- A terminal. On a Mac, the Terminal app. On Windows, PowerShell. In VS Code, the built-in terminal works well.
- About 90 minutes, or two sittings of 45.

No key yet? Every step runs with `--dry-run`, which walks the same path with a pretend Claude, so you can learn the shape of the lab first and add the key later.

## Step 0: Set up (10 minutes)

1. Get the files. Either click the green Code button on GitHub and choose Download ZIP, then unzip it, or run:

   ```
   git clone https://github.com/macfarlanem-cloud/claude-course-design-lab.git
   ```

2. Open a terminal inside the folder:

   ```
   cd claude-course-design-lab
   ```

3. Create a private workspace for the lab's libraries (a "virtual environment") and turn it on. This keeps the lab separate from anything else on your computer.

   Mac/Linux:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   Windows (PowerShell):
   ```
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   You will see `(.venv)` at the start of your prompt when it is on.

4. Install the two libraries the lab uses:

   ```
   pip install -r requirements.txt
   ```

5. Put your API key in place. Copy `.env.example` to a new file named `.env`, open it in any text editor, and paste your key after the equals sign. Save. (The `.gitignore` file makes sure this file is never uploaded anywhere.)

6. Run the readiness check:

   ```
   python step_0_check.py
   ```

Checkpoint: the last line says `Ready to go.` If not, the lines above it tell you exactly which item to fix.

## Step 1: One message in, one message out (15 minutes)

```
python step_1_hello.py
```

Open `step_1_hello.py` in a text editor while it runs. It is short on purpose. Find these five things in it:

- `client`: the connection to Claude, made once.
- `model`: which Claude you are talking to.
- `system`: the job description. Who should Claude be for this conversation?
- `messages`: the conversation so far, oldest first.
- `response`: what came back.

Checkpoint: you see a short, warm reply about first-week modules in the console.

Reflection: change `SYSTEM_PROMPT` to describe a different colleague (stricter, funnier, more Socratic, a peer rather than a partner). Run it again. Notice how much changes before you touched anything else. That is the lever educators are best at pulling, because describing the colleague you want is describing good teaching.

## Step 2: Give Claude a tool (25 minutes)

```
python step_2_tool.py
```

In Step 1, Claude only knew what was in the message. Now it can ask your computer to read a file. Watch the console. You will see four moments:

1. Your script tells Claude a tool exists: `read_file`, what it does, what it needs.
2. Claude decides it needs the tool and replies with a request: "run read_file on materials/sample_syllabus.md."
3. Your script runs the function and sends the contents back.
4. Claude, now holding the syllabus, writes its real answer.

Checkpoint: the console shows `Claude asked to run: read_file`, then an answer that clearly knows what is in the syllabus (it should name the course and notice the Week 6 case study).

Reflection: Claude never touched your files. Your script did, and only inside this folder (look at `read_project_file` in `lab_helpers.py` to see the guardrail). This is the whole idea of tool use: Claude asks, your code decides. When you hear "agents" and "MCP," this loop is what is underneath.

Try it: open `step_2_tool.py` and change the tool's `description`. Make it vague. Run again and see whether Claude still reaches for the tool. A tool description is a piece of teaching; clear ones get used well.

## Step 3: Load a Skill (30 minutes)

A Skill is a plain-text file, `SKILL.md`, that captures how an expert does a kind of work: the order to work in, the frameworks to apply, the checks to run before finishing. Open `skills/humanizing-course-design/SKILL.md` and read it first. It was written by an educator, and every line is a design decision you could argue with.

Run it twice.

First run, with no information about the learners:

```
python step_3_skill.py
```

Checkpoint: Claude reads the syllabus and then asks you about the learners instead of charging ahead. That is the Skill working. Its first rule is "learners first: do not invent a generic learner profile." The output is saved to `output/week6_first_run.md`.

Second run, pointing Claude at a learner profile:

```
python step_3_skill.py --with-learners
```

Checkpoint: `output/week6_module_plan.md` contains a complete Week 6 module that names the actual learners from `materials/learner_profile.md`, gives the assignment a purpose, task, and criteria, and ends with a "design notes" section that names the frameworks it used (UDL, TiLT, culturally responsive practice, accessibility). Open the file and check each of those.

Reflection: read the plan the way you would read a colleague's draft. Find one decision that is generic, or wrong for these learners, or wrong for the discipline. Only a teacher would catch it. Now find the line in `SKILL.md` you would change so it does not happen next time. That loop, judgment into instructions into better output, is the work.

## Step 4: Make it yours (as long as you like)

Three swaps, in order of effort:

1. Your syllabus. Replace `materials/sample_syllabus.md` with one of yours and update the week number in `USER_MESSAGE` inside `step_3_skill.py`.
2. Your learners. Rewrite `materials/learner_profile.md` for a real section. Describe people by role, place, and circumstance.
3. Your Skill. Copy the `skills/humanizing-course-design` folder, rename it, and edit `SKILL.md` to reflect how you design. The format is just a name, a description, and instructions. Point `load_skill(...)` in `step_3_skill.py` at your new folder.

## Bonus: the official Skills API (15 minutes, optional)

In Step 3 we pasted the Skill into the system prompt ourselves. The platform can also host Skills for you: upload the folder once, get an id, reference it from any request.

```
python bonus_skills_api.py
```

This one has no dry run and uses beta features, so names may shift; the script says where to look if it fails. Reflection: same Skill, two delivery methods. When would you want a Skill managed centrally for a whole department, and when would you want it in your own folder where you can edit it in a minute?

## Step 5: Publish it to Canvas (optional, 20 minutes)

Everything so far ends in a file. This step gives Claude a second tool, `create_canvas_page`, that creates a page in one of your Canvas courses through the Canvas API. Claude reads the Week 6 plan from Step 3, turns it into clean, accessible HTML, and asks your script to create the page. Your script is the only thing that talks to Canvas; Claude never sees your token.

Try the safe version first:

```
python step_5_canvas.py --dry-run
```

Checkpoint: the console shows two tool calls in order, `read_file` then `create_canvas_page`, and the result line begins with `DRY RUN. Would create an unpublished page`.

For the live version you need a Canvas course you own (a sandbox or a development course is ideal) and three more lines in `.env`: `CANVAS_BASE_URL` (your Canvas address, such as `https://yourcollege.instructure.com`), `CANVAS_TOKEN` (Canvas, then Account, then Settings, then New Access Token; treat it like a password), and `CANVAS_COURSE_ID` (the number in the course URL). Then run Step 3 with learners if you have not already, and:

```
python step_5_canvas.py
```

Checkpoint: Claude gives you a link to a new page in that course, and the page is unpublished. Open it, read it as a learner would, fix anything, and publish only when you are satisfied.

Reflection: the tool creates the page with `published: false`. That one line is where your judgment stays in the loop. Which other parts of your teaching would you hand to a tool only with a check like that in place?

## What to try next

- Add a third tool. A `list_files` tool that returns the names of files in `materials/` lets Claude discover documents instead of being told the path.
- Point the assistant at a folder of past discussion prompts and ask it to find the ones that never got replies.
- Swap the model in `lab_helpers.py` and compare. Try a faster model for drafts and a stronger one for the final pass.
- Wrap Step 3 in a small web form so a colleague can use it without a terminal.
- Read Anthropic's tool use and Skills guides at platform.claude.com/docs. Everything in this lab maps directly onto them.

## How this lab was built

This lab was built in Claude Code by Michelle Macfarlane, a community college agriculture professor and department chair, working as the designer and decision-maker with Claude writing the code. The learning outcomes, the step sequence, the checkpoints, the sample syllabus, the learner profile, and the Skill are hers; the Python is Claude's, reviewed line by line so that every piece can be explained and changed. That division of labor is the point of the lab. Content can be learned. Knowing what good teaching looks like before the AI produces anything is the expertise that makes the tool worth using.

Conventions you may notice: no em dashes anywhere, plain language over jargon, learners described by circumstance rather than by label, and every step verifiable by the person doing it.

## Files in this repo

| File | What it is |
|---|---|
| `step_0_check.py` | Readiness check, no API call |
| `step_1_hello.py` | One message, one reply |
| `step_2_tool.py` | Adds the `read_file` tool and the tool-use loop |
| `step_3_skill.py` | Adds the Skill; writes the module plan to `output/` |
| `step_5_canvas.py` | Optional: a second tool that creates an unpublished Canvas page from the plan |
| `bonus_skills_api.py` | Same Skill through the platform's Skills API |
| `lab_helpers.py` | Shared helpers, plus the pretend client used by `--dry-run` |
| `.env.example` | Where your API key (and optional Canvas settings) go, after you copy it to `.env` |
| `materials/` | Sample syllabus and learner profile (replace with yours) |
| `skills/humanizing-course-design/SKILL.md` | The Skill |
| `QUICK_REFERENCE.md` | One-page summary of the commands and concepts |
| `HOW_IT_WORKS.md` | One-page explanation of what is actually happening and why the lab is built this way |
| `docs/` | The tool-use loop diagram (SVG and PNG), free to reuse in slides or videos |

## License

MIT. Use it, remix it, teach with it. If you build something with it, I would love to hear about it.
