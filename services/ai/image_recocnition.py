from pathlib import Path


class ImageRecognitionService:
    def detect(self, image_path: str) -> dict:
        suffix = Path(image_path).suffix.lower()
        if suffix not in {".jpg", ".jpeg", ".png", ".webp"}:
            return {
                "status": "error",
                "data": None,
                "error": "Unsupported image format",
            }
        return {
            "status": "ok",
            "data": {"label": "food", "confidence": 0.75},
            "error": None,
        }
