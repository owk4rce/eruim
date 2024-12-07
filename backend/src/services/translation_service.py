from deep_translator import GoogleTranslator
from backend.src.utils.exceptions import ExternalServiceError


def translate_with_google(source_text, source_lang, target_lang):
    try:
        translated = GoogleTranslator(
            source=source_lang,
            target=target_lang
        ).translate(source_text)

        return translated

    except Exception as e:
        raise ExternalServiceError(f"Translation service error: {str(e)}")
