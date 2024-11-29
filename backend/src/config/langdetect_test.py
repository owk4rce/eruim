from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException


def test_language_detection():
    """Test language detection with different cases"""

    test_texts = [
        # Чистые тексты
        "Hello World",
        "Привет мир",
        "שלום עולם",

        # Смешанные тексты
        "Hello Мир",
        "Привет World",
        "Hello שלום",
        "שלום Привет",

        # Тексты с цифрами и символами
        "Hello World 123",
        "Привет мир 123",
        "שלום עולם 123",

        # Очень короткие тексты
        "Hi",
        "Хай",
        "הי"
    ]

    print("Testing language detection:")
    print("-" * 50)

    for text in test_texts:
        try:
            detected = detect(text)
            print(f"Text: {text}")
            print(f"Detected language: {detected}")
            print()

        except LangDetectException as e:
            print(f"Error detecting language for '{text}': {str(e)}")
            print()


if __name__ == "__main__":
    test_language_detection()