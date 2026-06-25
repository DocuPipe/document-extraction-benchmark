# Document Extraction Benchmark

A public, reproducible head-to-head benchmark for document data extraction, built from real-world public documents with hand-verified labels and deliberately hard structure: line-item arrays, multipage tables, eleven languages, right-to-left and CJK scripts, rotated scans, handwriting, and ten file types.

This repository contains everything needed to inspect and rerun the benchmark: the source documents, the schemas, the hand-verified ground-truth labels, both engines' raw extraction output, the scorer, and a full source manifest ([SOURCES.md](SOURCES.md)).

Full write-up: **[We tied Extend on the easy benchmark; the hard documents told a different story](https://www.docupipe.ai/blog/docupipe-vs-extend-benchmark)**.

## Results

50 hard public documents, field-level accuracy, both engines scored with the same array-aware scorer against the same labels:

| System | Accuracy |
|---|---:|
| DocuPipe (high effort) | **97.24%** |
| DocuPipe (standard effort) | **96.00%** |
| Extend | **92.52%** |

On clean, simple documents both systems often reach 100%. The gap opens on structural cases: multilingual and right-to-left documents, array-heavy statements, multipage context, and non-PDF file types. Per-document scores are in [`results/summary.json`](results/summary.json).

For context, on Extend's own flat, single-page [RealDoc-Bench](https://www.extend.ai/resources/realdocbench) QA set the two systems were effectively tied (DocuPipe 95.31% vs Extend's best configuration 95.15%). That benchmark is not reproduced here because its documents and answer key are published separately by Extend; this repository is the harder structural benchmark we built. The blog post covers both.

## What is in the benchmark

50 documents spanning:

- **File types (10):** pdf, jpeg, png, tiff, xlsx, csv, xml, txt, docx, html
- **Languages (11):** English, Hebrew, Japanese, Chinese, Arabic, French, German, Portuguese, Dutch, Italian, Spanish
- **Structure:** invoices, bank and brokerage statements, utility bills, annual reports, payslips, purchase orders, waybills, lab and discharge reports, engineering drawings, insurance declarations, tax forms, and more, most with at least one array, multipage, nested, or table feature.

Every label was authored for this benchmark and verified field-by-field against the source document. Disagreements between the two engines and our labels were audited before publishing: where an engine's answer was defensible under the schema, the schema or label was fixed rather than scoring the engine down. The goal is to measure extraction quality, not to reward labels that happen to favor one engine.

## Repository layout

```
scorer.py                 standalone array-aware scorer (stdlib only)
documents/<doc_id>.<ext>  the 50 source documents
labels/<doc_id>.json      hand-verified ground truth
schemas/<doc_id>.json     the json schema applied to each document
results/
  docupipe_high/<doc_id>.json     DocuPipe high-effort extraction + score
  docupipe_standard/<doc_id>.json DocuPipe standard-effort extraction + score
  extend/<doc_id>.json            Extend extraction + score
  summary.json                    per-document and aggregate scores
sources.json              machine-readable document manifest (sources + licenses)
SOURCES.md                human-readable document manifest
scripts/
  run_extend.py           run a document + schema through Extend
  score_all.py            score every engine's results against the labels
```

## How scoring works

`scorer.py` does field-level scoring designed for schema-shaped extraction. Numbers are cast to a common type and strings are normalized for benign whitespace and punctuation differences before comparison. Arrays are scored by matching extracted rows to labeled rows with a greedy best-pair assignment, so two systems that return the same rows in a different order both score correctly. Every leaf field carries equal weight; a blank field in both the label and the result is skipped rather than counted as a free match.

Reproduce the published aggregates from the committed results:

```bash
python scripts/score_all.py
# docupipe_high ~0.9724, docupipe_standard ~0.9600, extend ~0.9252
```

## Reproducing an engine's run

The source documents are in `documents/`, paired with their `schemas/<doc_id>.json`.

1. **Run Extend** on a document with its schema:

   ```bash
   export EXTEND_API_KEY=...   # your own Extend workspace key
   python scripts/run_extend.py documents/UnG6cLfP.pdf schemas/UnG6cLfP.json /tmp/out.json
   ```

2. **Run DocuPipe** by applying the same `schemas/<doc_id>.json` to the same document through the DocuPipe API (an account and API key are required). See the [DocuPipe API docs](https://docs.docupipe.ai).

3. **Score** any engine's output against the labels with `scorer.py` or `scripts/score_all.py`.

## Licensing

- **Code** (`scorer.py`, `scripts/`): MIT, see [LICENSE](LICENSE).
- **Labels, schemas, results**: CC BY 4.0.
- **Documents** (`documents/`): each retains its own license; the original source and license for every document are listed in [SOURCES.md](SOURCES.md). They are included here for research and evaluation. If you are a rights-holder and want a document removed, open an issue.
