# Demo Script

## Start

```bash
cd EMKA
docker compose up --build
```

Open:

- Workspace: `http://127.0.0.1:5173`
- Health: `http://127.0.0.1:8000/health`

## Upload

1. Use the left upload panel.
2. Upload one or more files:
   - `notes.txt`
   - `metrics.csv`
   - `screenshot.png`
3. Confirm each uploaded document appears in the document list with a modality label.

## Ask

Use the chat panel with a question like:

```text
Summarize the uploaded materials and cite the most relevant sources.
```

Expected result:

- The center panel shows `answer`.
- The report panel shows report markdown text.
- Retrieved docs include title, modality, score, snippet, and citation.
- Table results may include row ranges.
- Image results may include OCR confidence.

## Inspect

Use the right panels to inspect:

- Trace route, confidence, plan, status, and latency.
- Retrieved docs and citations.
- Tool calls with success and latency.
- Memory reads/writes.
- Ingestion ops empty state or recorded operations when available.

## API Smoke Commands

```bash
curl http://127.0.0.1:8000/health
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"00000000-0000-0000-0000-000000000101\",\"conversation_id\":\"00000000-0000-0000-0000-000000000201\",\"message\":\"Summarize uploaded documents\"}"
```
