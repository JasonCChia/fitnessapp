from services.ai.chat_text import ChatTextService
from services.ai.image_recocnition import ImageRecognitionService


class AIService:
    def __init__(self):
        self.chat = ChatTextService()
        self.image = ImageRecognitionService()

    def chat_text(self, text: str) -> dict:
        return self.chat.ask(text)

    def recognize_image(self, image_path: str) -> dict:
        return self.image.detect(image_path)
