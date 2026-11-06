import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

STEPS = [
    os.path.join(ROOT, "sample-data", "generate_dummy_data.py"),
    os.path.join(HERE, "clean.py"),
    os.path.join(HERE, "score.py"),
    os.path.join(HERE, "report.py"),
]

if "--with-research" in sys.argv:
    STEPS.insert(2, os.path.join(HERE, "research.py"))
else:
    print("Using saved research results (add --with-research to call the API again)")

for step in STEPS:
    print(f"\n=== {os.path.relpath(step, ROOT)} ===")
    subprocess.run([sys.executable, step], check=True)
