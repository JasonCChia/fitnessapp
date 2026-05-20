class ChatTextService:
    def ask(self, user_text: str) -> dict:
        if not user_text:
            return {"status": "error", "data": None, "error": "Empty prompt"}
        return {
            "status": "ok",
            "data": {"reply": f"AI placeholder response for: {user_text}"},
            "error": None,
        }
