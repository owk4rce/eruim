from deep_translator import GoogleTranslator
from backend.src.utils.exceptions import ExternalServiceError

import logging

logger = logging.getLogger("backend")


def translate_with_google(source_text, source_lang, target_lang):
    """
    Translate text using Google Translate API via deep_translator library.

    Handles translation requests for various content types including:
    - Venue/event names and descriptions
    - Address translations
    - Any other multilingual content in the application

    Args:
        source_text (str): Text to translate
        source_lang (str): Source language code (e.g., 'en', 'ru', 'iw' for Hebrew)
        target_lang (str): Target language code

    Returns:
        str: Translated text

    Raises:
        ExternalServiceError: If translation fails for any reason

    Note:
        - Uses 'iw' as language code for Hebrew (Google Translate requirement)
        - Free tier of Google Translate is used through deep_translator
    """
    logger.debug(f"Attempting translation from {source_lang} to {target_lang}.")

    try:
        translated = GoogleTranslator(
            source=source_lang,
            target=target_lang
        ).translate(source_text)

        logger.info(f"Successfully translated text from {source_lang} to {target_lang}")

        return translated

    except Exception as e:
        raise ExternalServiceError(f"Translation service error: {str(e)}")
