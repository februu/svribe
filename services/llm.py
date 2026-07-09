import asyncio
import json
from google import genai
from google.genai.errors import ServerError
from typing import Iterable
from config import config
from models.message_category import MessageCategory

_client = genai.Client(api_key=config.GEMINI_API_KEY)

_BAD_RESPONSE_DELAYS = [0.5, 1.0]  # model returned unexpected data (BadResponseError)
_SERVER_ERROR_DELAYS = [5.0, 15.0]  # 503 / server unavailable (ServerError)


class BadResponseError(Exception):
    """Raised when the model returns an unexpected response."""


class ConnectionError(Exception):
    """Raised when there is a connection error with the LLM."""


async def generate_response(content: str, categories_json: str) -> str:
    """Generates a response from the Gemini API for categorizing the given content."""
    try:
        response = await _client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Text to categorize:\n{content}",
            config=genai.types.GenerateContentConfig(
                system_instruction=f"""You are a classification assistant.
    Your job is to classify a given text, link or file extensions into exactly one of the following categories:
    {categories_json}

    Rules:
    - Reply with ONLY the category name, exactly as written above
    - Do not add punctuation, explanation, or extra words
    - If no category fits, reply with: <none>""",
                temperature=0.1,
            ),
        )
    except ServerError:
        raise ConnectionError("Error connecting to the LLM")

    if not response.text:
        raise BadResponseError("No text returned from model")

    return response.text


async def get_category(
    content: str, available_categories: Iterable[MessageCategory]
) -> MessageCategory | None:
    """Returns the category that best fits the given text, or None if no category matches."""

    categories = list(available_categories)
    if not categories:
        return None

    categories_formatted = json.dumps(
        [{"name": c.name, "desc": c.description} for c in categories], indent=2
    )
    content = content.lower()

    for attempt in range(3):
        try:
            response = await generate_response(content, categories_formatted)
            response = response.strip().lower()

            if response == "<none>":
                return None

            for category in categories:
                if category.name.lower() == response:
                    return category

            raise BadResponseError(f"Unexpected response from model: {response}")

        except ConnectionError:
            if attempt < 2:
                await asyncio.sleep(_SERVER_ERROR_DELAYS[attempt])
            continue
        except BadResponseError:
            if attempt < 2:
                await asyncio.sleep(_BAD_RESPONSE_DELAYS[attempt])
            continue
    return None
