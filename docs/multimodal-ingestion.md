# Multimodal Ingestion

## Flow

```text
UploadFile
  -> ModalityDetector
  -> TextParser | TableParser | OCRParser
  -> Normalizer
  -> DocumentRepository
  -> RAGPipeline
  -> Chunker
  -> DeterministicEmbeddingProvider
  -> MilvusVectorStore
```

## Supported Files

- `txt` and `md`: decoded as text.
- `pdf`: parsed page by page with PyPDF2.
- `docx`: extracts paragraphs and table cells with python-docx.
- `csv`: parsed with the Python csv module.
- `xlsx`: parsed with openpyxl.
- `png`, `jpg`, `jpeg`: opened with Pillow for image metadata and stable mock OCR text.

## Output Shape

Every ingested document produces:

- `modality`: `text`, `table`, or `image`.
- `parser`: `text_parser`, `table_parser`, or `ocr_parser`.
- `content`: normalized text used by RAG.
- `metadata`: parser metadata such as page count, sheet names, row ranges, image dimensions, or OCR confidence.

## Citations

- Text citations reference the document title and chunk index.
- Table citations include `row_range` when available.
- Image citations include `ocr_confidence` when available.

## Current Boundary

OCR is intentionally lightweight for this phase: the parser validates image bytes and records width, height, and format, but OCR text is deterministic mock output. This keeps Docker demo setup small and repeatable.
