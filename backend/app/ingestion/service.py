from dataclasses import dataclass, field
from pathlib import Path

from backend.app.ingestion.detector import detect_modality, parser_name_for
from backend.app.ingestion.normalizer import normalize_content
from backend.app.ingestion.ocr_parser import parse_image_file
from backend.app.ingestion.table_parser import parse_table_file
from backend.app.ingestion.text_parser import parse_text_file


class EmptyFileError(ValueError):
    pass


@dataclass
class IngestedDocument:
    title: str
    modality: str
    content: str
    metadata: dict = field(default_factory=dict)
    parser: str = "text_parser"


class IngestionService:
    def ingest(self, filename: str, content: bytes, content_type: str | None = None) -> IngestedDocument:
        if not content:
            raise EmptyFileError("empty file")

        modality = detect_modality(filename)
        parser = parser_name_for(filename)
        suffix = Path(filename or "").suffix.lower()
        title = Path(filename or "uploaded").name
        metadata = {
            "filename": title,
            "content_type": content_type or "application/octet-stream",
            "parser": parser,
            "modality": modality,
            "extension": suffix,
        }

        if modality == "text":
            parsed = parse_text_file(title, content, metadata)
        elif modality == "table":
            parsed = parse_table_file(title, content, metadata)
        elif modality == "image":
            parsed = parse_image_file(title, content, metadata)
        else:
            parsed = self._decode_text(content)

        normalized = normalize_content(parsed, metadata)

        return IngestedDocument(
            title=title,
            modality=modality,
            content=normalized.content,
            metadata=normalized.metadata,
            parser=parser,
        )

    def _decode_text(self, content: bytes) -> str:
        return content.decode("utf-8", errors="replace").strip()

    def _placeholder_text(self, title: str, modality: str, parser: str, content: bytes) -> str:
        size = len(content)
        return (
            f"{title} has been accepted as {modality} content by {parser}. "
            f"Deep parsing is scheduled for Task-010. Raw file size: {size} bytes."
        )
