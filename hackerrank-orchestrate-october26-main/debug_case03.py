import runpy
from pathlib import Path

m = runpy.run_path("code/main.py")
dataset = Path("dataset")

requests = m["read_csv"](dataset / "sample_deletion_requests.csv")
identities = m["read_csv"](dataset / "user_identities.csv")
audits = m["read_csv"](dataset / "user_audit_log.csv")
activities = m["read_csv"](dataset / "system_activity.csv")
rules = m["read_csv"](dataset / "deletion_rules.csv")
observations, _ = m["build_observations"](dataset)

req = next(r for r in requests if r["case_id"] == "case_03")
uid, aliases, emails, phones = m["resolve_identity"](
    req["email"], req["audit_at"], identities, audits
)

print("IDENTITY:", uid)
print("EMAILS:", emails)

matched = [
    o for o in observations
    if m["matches_user"](o, uid, aliases, emails, phones, req["audit_at"])
    and o.resource_id == "account_7566"
]

print("\nMATCHED OBSERVATIONS:")
for o in matched:
    print({
        "evidence": o.file_id,
        "system": o.system_id,
        "resource": o.resource_id,
        "category": o.category,
        "state": o.explicit_state,
        "captured": o.captured_at,
        "observed": o.observed_at,
        "raw": o.raw[:180]
    })

print("\nCASE OUTPUT:")
print(m["case_output"](req, observations, identities, audits, activities, rules))
