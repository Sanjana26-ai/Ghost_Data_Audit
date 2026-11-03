GHOST DATA — LOCAL DELETION AUDIT WEBSITE

FAST SETUP (Windows):
1. Extract this ZIP.
2. Copy app.py, templates\, static\ and requirements.txt into:
   hackerrank-orchestrate-october26-main
   (the same folder containing test_sample.py and dataset\).
3. Open PowerShell in that project folder and run:
   py -m pip install -r requirements.txt
   py app.py
4. Open http://127.0.0.1:5000

The dashboard compares dataset\sample_output.csv with sample_actual.csv.
"Run test script" executes test_sample.py locally.
Nothing is uploaded. This is a local dashboard and does not replace the audit logic in code\main.py.
