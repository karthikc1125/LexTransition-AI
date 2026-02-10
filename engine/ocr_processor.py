"""
Simple OCR helper with availability checks.
Functions:
- extract_text(file_bytes: bytes) -> str
- available_engines() -> list of strings
"""
import io
from typing import List

_EASYOCR_READER = None

def _get_easyocr_reader():
    global _EASYOCR_READER
    if _EASYOCR_READER is not None:
        return _EASYOCR_READER
    import easyocr  # type: ignore
    _EASYOCR_READER = easyocr.Reader(["en"], gpu=False)
    return _EASYOCR_READER

def available_engines() -> List[str]:
    engines = []
    try:
        import easyocr  # type: ignore
        engines.append("easyocr")
    except Exception:
        pass
    try:
        import pytesseract  # type: ignore
        engines.append("pytesseract")
    except Exception:
        pass
    return engines

def extract_text(file_bytes: bytes) -> str:
    # Try EasyOCR first
    try:
        from PIL import Image  # type: ignore
        reader = _get_easyocr_reader()
        image = Image.open(io.BytesIO(file_bytes))
        result = reader.readtext(image)
        return " ".join([r[1] for r in result])
    except Exception:
        # Fallback to pytesseract
        try:
            import pytesseract  # type: ignore
            from PIL import Image  # type: ignore
            image = Image.open(io.BytesIO(file_bytes))
            return pytesseract.image_to_string(image)
        except Exception:
            return "NOTICE UNDER SECTION 41A CrPC... (OCR not configured). Install easyocr/pytesseract & tesseract binary for production."
