import asyncio
from google import genai
from google.genai.errors import ServerError
from typing import Iterable
from config import config

_client = genai.Client(api_key=config.GEMINI_API_KEY)

_BAD_RESPONSE_DELAYS = [0.5, 1.0]  # model returned something unexpected
_SERVER_ERROR_DELAYS = [5.0, 15.0]  # 503 / server unavailable


async def get_category_from_text(text: str, categories: Iterable[str]) -> str | None:
    """Returns the category that best fits the given text, or None if no category matches."""
    text = text.lower()
    categories = [c.lower() for c in categories]
    categories_formatted = "\n".join(f"- {c}" for c in categories)

    for attempt in range(3):
        try:
            response = await _client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Text to categorize:\n{text}",
                config=genai.types.GenerateContentConfig(
                    system_instruction=f"""You are a classification assistant.
Your job is to classify a given text, link or file extensions into exactly one of the following categories:
{categories_formatted}

Rules:
- Reply with ONLY the category name, exactly as written above
- Do not add punctuation, explanation, or extra words
- If no category fits, reply with: none""",
                    temperature=0.1,
                ),
            )
        except ServerError:
            if attempt < 2:
                await asyncio.sleep(_SERVER_ERROR_DELAYS[attempt])
            continue

        if response.text:
            result = response.text.strip().lower()
            if result in categories:
                return result

        if attempt < 2:
            await asyncio.sleep(_BAD_RESPONSE_DELAYS[attempt])

    return None
