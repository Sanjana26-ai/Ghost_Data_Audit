
import csv
import subprocess
import sys
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash

CODE_DIR = Path(__file__).resolve().parent
ROOT = CODE_DIR.parent
DATASET_DIR = ROOT / "dataset"

app = Flask(__name__)
app.secret_key = "ghost-data-local-dashboard"


def read_csv(path):
    if not path.exists():
        return []

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))
    except (OSError, UnicodeError, csv.Error) as exc:
        app.logger.error("Could not read %s: %s", path, exc)
        return []


def get_value(row, *names):
    """Read a CSV value while allowing common column-name variations."""
    normalized = {
        str(key).strip().lower().replace(" ", "_"): value
        for key, value in row.items()
        if key is not None
    }

    for name in names:
        value = normalized.get(name.lower().replace(" ", "_"))
        if value is not None:
            return str(value).strip()

    return ""


def load_actual_results():
    # Prefer the main engine's configured output location.
    candidates = [
        ROOT / "output.csv",
        DATASET_DIR / "output.csv",
        ROOT / "sample_actual.csv",
        CODE_DIR / "sample_actual.csv",
    ]

    for path in candidates:
        if path.exists():
            return read_csv(path), path

    return [], None


def normalize_steps(value):
    return " ".join((value or "").split()).strip()


@app.route("/")
def index():
    expected_path = DATASET_DIR / "sample_output.csv"
    expected = read_csv(expected_path)
    actual, actual_path = load_actual_results()

    actual_map = {}
    for row in actual:
        case_id = get_value(row, "case_id", "case id", "id")
        if case_id:
            actual_map[case_id] = row

    cases = []

    for exp in expected:
        case_id = get_value(exp, "case_id", "case id", "id")
        result = actual_map.get(case_id, {})

        expected_status = get_value(
            exp, "deletion_status", "status", "expected_status", "expected"
        )
        actual_status = get_value(
            result, "deletion_status", "status", "actual_status", "actual"
        )

        expected_steps = get_value(
            exp, "steps_json", "steps", "verification_steps", "step"
        )
        actual_steps = get_value(
            result, "steps", "verification_steps", "step"
        )

        has_actual = bool(result)
        status_match = (
            has_actual
            and expected_status.casefold() == actual_status.casefold()
        )
        steps_match = (
            has_actual
            and normalize_steps(expected_steps)
            == normalize_steps(actual_steps)
        )

        cases.append({
            "case_id": case_id or "Unknown",
            "expected": expected_status or "—",
            "actual": actual_status if has_actual else "NOT RUN",
            "expected_steps": expected_steps,
            "steps": actual_steps if has_actual else "",
            "has_actual": has_actual,
            "status_match": status_match,
            "steps_match": steps_match,
        })

    processed = sum(case["has_actual"] for case in cases)
    status_matches = sum(case["status_match"] for case in cases)
    step_matches = sum(case["steps_match"] for case in cases)
    review_count = sum(
        case["has_actual"]
        and not (case["status_match"] and case["steps_match"])
        for case in cases
    )

    return render_template(
        "index.html",
        cases=cases,
        total=len(cases),
        processed=processed,
        status_matches=status_matches,
        step_matches=step_matches,
        review_count=review_count,
        dataset_found=expected_path.exists(),
        actual_found=actual_path is not None,
        actual_file=str(actual_path.relative_to(ROOT))
        if actual_path and actual_path.is_relative_to(ROOT)
        else (actual_path.name if actual_path else ""),
    )


@app.post("/run-engine")
def run_engine():
    script = CODE_DIR / "main.py"

    if not script.exists():
        flash("Engine not found: code/main.py", "error")
        return redirect(url_for("index"))

    try:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )

        if result.returncode == 0:
            output = result.stdout.strip() or "Engine finished."
            flash("Engine completed.\n" + output[-2500:], "success")
        else:
            output = result.stderr.strip() or result.stdout.strip()
            flash(
                "Engine failed (exit code "
                + str(result.returncode)
                + ").\n"
                + (output[-2500:] or "No error details were returned."),
                "error",
            )

    except subprocess.TimeoutExpired:
        flash("Engine timed out after 180 seconds.", "error")
    except OSError as exc:
        flash("Could not start engine: " + str(exc), "error")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
