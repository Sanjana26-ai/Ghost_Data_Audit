# Token Usage and Cost Report

## Final full-dataset run

- Run command: `python3 code/main.py`
- Input requests processed: 518
- Output file: repository-root `output.csv`
- LLM used: **No**
- Model provider/name: **Not applicable — no model API or local LLM was invoked**
- Model calls: 0
- Input tokens: 0
- Output tokens: 0
- Total tokens: 0
- Average tokens per request: 0
- Estimated total model cost: **US$0.00**
- Estimated model cost per request: **US$0.00**

## Method and assumptions

The current implementation is a deterministic Python pipeline using local CSV, JSON, SQLite-compatible SQL and text processing. Optional `pdftotext` and `tesseract` commands are used for document/image extraction; they are not language-model calls and do not produce LLM token usage. No external model provider, model name, token meter, or provider pricing schedule applies to this run.

The zero-token and zero-cost values mean no LLM was used; they are not estimates of CPU time, OCR runtime, or engineering effort. If a future version integrates an LLM, rerun the full 518-case dataset and replace this report with measured per-model input/output tokens, call counts, pricing assumptions, total cost, average cost per request and overall totals. Do not infer or fabricate token counts.
