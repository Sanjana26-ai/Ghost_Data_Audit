# Evaluation Report — Ghost Data Still Exists

## Evaluation methodology

The solution was run against the participant-facing 518-case dataset. Validation covered the required CSV header and column order, row count, sorted unique case IDs, allowed statuses, JSON parsing, exact step fields, consecutive step numbering, operation/phase/state combinations, phase and operation ordering, known evidence identifiers, evidence presence for findings and completed-case verification, and empty evidence IDs for proposed remediation/future verification.

The public `sample_deletion_requests.csv` (32 cases) was also processed and compared with `sample_output.csv`. These public samples are diagnostic examples; they are not the 518-case evaluation set. Hidden canonical labels for the 518 evaluation requests are unavailable, so full-dataset canonical accuracy cannot be reported.

## Results

- Full-dataset execution: **completed**; generated root-level `output.csv`.
- Full-dataset output: **518 data rows**, header `case_id,deletion_status,steps_json`, sorted by `case_id`.
- Structural validator: **passed** on the generated output.
- Custom regression tests: **6 passed, 0 failed** in the latest recorded test run.
- Public sample deletion-status accuracy: **25/32 (78.1%)**.
- Public sample exact step-array match: **2/32 (6.2%)**.
- Public sample step-set precision: **102/144 (70.8%)**.
- Public sample step-set recall: **102/193 (52.8%)**.
- Public sample field accuracy for operation, state and evidence ID on resource/phase anchors: **315/648 (48.6%)**.

The public sample metrics show that the implementation is structurally valid but still has substantial gaps in reconstructing the exact canonical resource list and ordered step arrays. Structural validity must not be interpreted as high deletion-audit accuracy.

## Case-level, row-level, field-level and sequence accuracy

- **Case-level canonical accuracy on the 518 main requests:** unavailable; hidden canonical outputs were not supplied.
- **Row-level exact-match accuracy on the 32 public samples:** 2/32 (6.2%), where a row must match both status and the complete ordered JSON array.
- **Field-level public-sample accuracy:** 315/648 (48.6%) across operation, state and evidence ID for matched phase/system/resource anchors; unmatched anchors count as incorrect fields.
- **Sequence accuracy on the 32 public samples:** 2/32 (6.2%) exact ordered arrays.
- **Canonical sequence accuracy on the 518 main requests:** unavailable.

## Additional evaluation cases created for this implementation

1. **Multilingual deletion intent:** Portuguese `exclusão`, Korean `삭제`, and French `suppression définitive du compte` must be recognized as deletion requests.
2. **Non-deletion correction/marketing request:** “Please correct my email address” and “Please unsubscribe me from marketing newsletters” must not be treated as deletion requests.
3. **Policy special treatment:** account tombstones use redaction, attributable analytics records use anonymization, and backup archives follow the retention/restore-blocking policy.

These are custom unit/regression cases, not hidden-canonical end-to-end cases. The test runner also checks output structure, step numbering/order, and `NOT_APPLICABLE` serialization.

## Failures found and improvements made

- The initial resource parser accepted non-resource strings such as service names as resource IDs. The parser was tightened to require recognized resource prefixes with numeric suffixes.
- Identity matching initially allowed substring collisions between user IDs. Matching was changed to use token boundaries.
- Deletion intent classification missed Portuguese, Korean and French variants. Multilingual patterns were added, and explicit “do not delete” requests are handled as non-deletion.
- Policy treatment initially risked treating already-anonymized analytics and retained backups as deletable. Policy logic was revised to retain the appropriate category action and separately assess exposure/restore risk.
- State reconstruction uses audit-time cutoffs and ignores later-captured evidence for the current case.

## Remaining limitations and uncertainty

- The sample metrics remain below an acceptable high-accuracy target, especially for complete ordered step arrays.
- Some anonymous records cannot be confidently attributed when the supplied evidence omits all stable links; the current deterministic approach may miss those associations.
- PDF and image extraction depends on local `pdftotext` and `tesseract` availability and OCR quality.
- Multilingual intent handling is rule-based and not a complete language-understanding system.
- The solution does not call an LLM or external API. It therefore does not provide model-based semantic interpretation of ambiguous evidence.
- No canonical score for the 518 hidden evaluation cases, hidden score, or leaderboard rank is known.

## Recommendation

Treat this version as a reproducible baseline, not a verified high-scoring final solution. The next highest-value improvement is to build a richer normalized evidence graph and review every public-sample mismatch, then add regression tests for each corrected relationship and policy decision before another full run.
