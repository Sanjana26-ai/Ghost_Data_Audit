import runpy
from pathlib import Path

namespace = runpy.run_path("code/main.py")
requests = namespace["read_csv"](Path("dataset/sample_deletion_requests.csv"))
identities = namespace["read_csv"](Path("dataset/user_identities.csv"))
audits = namespace["read_csv"](Path("dataset/user_audit_log.csv"))
activities = namespace["read_csv"](Path("dataset/system_activity.csv"))
rules = namespace["read_csv"](Path("dataset/deletion_rules.csv"))
observations, _ = namespace["build_observations"](Path("dataset"))

results = [
    namespace["case_output"](r, observations, identities, audits, activities, rules)
    for r in requests
]

import csv
with open("sample_actual.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["case_id", "deletion_status", "steps_json"])
    writer.writeheader()
    writer.writerows(sorted(results, key=lambda x: x["case_id"]))

print("Sample cases processed:", len(results))
print("Created sample_actual.csv")
