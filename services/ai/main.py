from flask import current_app

from services.ai.chat_text import ChatTextService
from services.ai.image_recocnition import ImageRecognitionService


class AIService:
    def __init__(self):
        self.chat = ChatTextService()
        self.image = ImageRecognitionService()

    def resolve_provider(self, user: dict | None = None) -> dict:
        return {
            "provider": "groq",
            "api_key": current_app.config.get("GROQ_API_KEY", ""),
            "model": current_app.config.get("GROQ_MODEL", "openai/gpt-oss-120b"),
        }

    def revise_proposal(
        self,
        *,
        provider: str,
        api_key: str,
        model: str,
        feedback: str,
        target_calories: int,
        target_protein_g: int,
        target_carbs_g: int,
        target_fat_g: int,
        sleep_target_hours: float,
    ) -> dict:
        system_prompt = (
            "You are a fitness and nutrition assistant. "
            "Return ONLY valid JSON object with keys: "
            "target_calories,target_protein_g,target_carbs_g,target_fat_g,sleep_target_hours,workout_preview,notes. "
            "workout_preview must be array with 4 short strings."
        )
        user_prompt = (
            f"Current daily targets:\n"
            f"- calories: {target_calories}\n"
            f"- protein_g: {target_protein_g}\n"
            f"- carbs_g: {target_carbs_g}\n"
            f"- fat_g: {target_fat_g}\n"
            f"- sleep_target_hours: {sleep_target_hours}\n\n"
            f"User feedback for revision:\n{feedback}\n\n"
            "Adjust targets and workout preview based on feedback while staying realistic and safe."
        )
        temperature = current_app.config.get("GROQ_TEMPERATURE", 1) if provider == "groq" else 0.2
        max_tokens = (
            current_app.config.get("GROQ_MAX_COMPLETION_TOKENS", 8192)
            if provider == "groq"
            else 800
        )
        return self.chat.ask_json(
            provider=provider,
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def analyze_food_photo(
        self,
        *,
        provider: str,
        api_key: str,
        model: str,
        image_path: str,
    ) -> dict:
        system_prompt = (
            "You are a nutrition estimator. "
            "Return ONLY valid JSON object with keys: "
            "label,confidence,estimated_calories,estimated_protein_g,estimated_carbs_g,estimated_fat_g. "
            "confidence must be between 0 and 1."
        )
        user_prompt = (
            "Analyze this food image and estimate calories and macros for one typical serving."
        )
        return self.image.detect(
            provider=provider,
            api_key=api_key,
            model=model,
            image_path=image_path,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=700,
        )
