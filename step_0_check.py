"""
Step 0: Is everything ready?

Run:  python step_0_check.py

This step makes no API call. It checks that Python can see the two
libraries the lab needs and that your API key is in place.
"""

import os
import sys
from pathlib import Path

ready = True

# 1. Python version
if sys.version_info < (3, 10):
    print("Python 3.10 or newer is needed. You have", sys.version.split()[0])
    ready = False
else:
    print("Python version:", sys.version.split()[0], "(good)")

# 2. Libraries
for library in ("anthropic", "dotenv"):
    try:
        __import__(library)
        print(f"Library '{library}': installed")
    except ImportError:
        print(f"Library '{library}': MISSING. Run: pip install -r requirements.txt")
        ready = False

# 3. API key in .env
env_file = Path(__file__).resolve().parent / ".env"
if env_file.is_file():
    from dotenv import load_dotenv
    load_dotenv(env_file)
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key.startswith("sk-ant-"):
        print("API key: found in .env (starts with sk-ant-)")
    else:
        print("API key: .env exists but ANTHROPIC_API_KEY looks empty or wrong")
        ready = False
    canvas = [os.environ.get(k, "") for k in ("CANVAS_BASE_URL", "CANVAS_TOKEN", "CANVAS_COURSE_ID")]
    if all(canvas):
        print("Canvas settings: found (only needed for the optional Step 5)")
    else:
        print("Canvas settings: not set (fine unless you want the optional Step 5)")
else:
    print("API key: no .env file yet. Copy .env.example to .env and paste your key in.")
    print("         (You can still run every step with --dry-run.)")
    ready = False

print()
print("Ready to go." if ready else "Not quite ready. Fix the items marked above, then run this again.")
