import pytest

from backend.app.ingestion.detector import UnsupportedFileTypeError, detect_modality, parser_name_for


@pytest.mark.parametrize(
    ("filename", "modality", "parser"),
    [
        ("note.txt", "text", "text_parser"),
        ("readme.md", "text", "text_parser"),
        ("report.pdf", "text", "text_parser"),
        ("brief.docx", "text", "text_parser"),
        ("risk.csv", "table", "table_parser"),
        ("sheet.xlsx", "table", "table_parser"),
        ("screen.png", "image", "ocr_parser"),
        ("photo.jpg", "image", "ocr_parser"),
        ("scan.jpeg", "image", "ocr_parser"),
    ],
)
def test_detector_maps_supported_extensions(filename, modality, parser):
    assert detect_modality(filename) == modality
    assert parser_name_for(filename) == parser


def test_detector_rejects_unsupported_extension():
    with pytest.raises(UnsupportedFileTypeError):
        detect_modality("archive.zip")
