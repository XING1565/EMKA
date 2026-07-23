from pathlib import Path


class UnsupportedFileTypeError(ValueError):
    pass


TEXT_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}
TABLE_EXTENSIONS = {".csv", ".xlsx"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def detect_modality(filename: str) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        return "text"
    if suffix in TABLE_EXTENSIONS:
        return "table"
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    raise UnsupportedFileTypeError(f"unsupported file type: {suffix or '<none>'}")


def parser_name_for(filename: str) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        return "text_parser"
    if suffix in TABLE_EXTENSIONS:
        return "table_parser"
    if suffix in IMAGE_EXTENSIONS:
        return "ocr_parser"
    raise UnsupportedFileTypeError(f"unsupported file type: {suffix or '<none>'}")
