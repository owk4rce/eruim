from deep_translator import (
    GoogleTranslator,
    MyMemoryTranslator,
    LingueeTranslator,
    PonsTranslator
)
from time import sleep


def test_translations():
    """Compare different translators"""

    test_texts = [
        # Addresses
        "שדרות רגר 41",
        "שדרות שאול המלך 27",
        "שדרות בן גוריון 12",
        "שדרות הנשיא 15",
        "שדרות ירושלים 20",
        # Description
        "המשכן לאמנויות הבמה בבאר שבע הוא המרכז התרבותי המרכזי באזור הנגב, מארח הצגות תיאטרון, קונצרטים ואירועי תרבות אחרים"
    ]

    # Test Google Translator
    print("Testing with Google Translator:")
    print("-" * 50)
    for text in test_texts:
        try:
            en_result = GoogleTranslator(source='iw', target='en').translate(text)
            print(f"Original: {text}")
            print(f"To English: {en_result}")

            ru_result = GoogleTranslator(source='iw', target='ru').translate(text)
            print(f"To Russian: {ru_result}")
            print()

        except Exception as e:
            print(f"Error with Google: {str(e)}")
            print()

        sleep(1)

    # Test MyMemory Translator
    print("\nTesting with MyMemory Translator:")
    print("-" * 50)
    for text in test_texts:
        try:
            en_result = MyMemoryTranslator(source='he-IL', target='en-GB').translate(text)
            print(f"Original: {text}")
            print(f"To English: {en_result}")

            ru_result = MyMemoryTranslator(source='he-IL', target='ru-RU').translate(text)
            print(f"To Russian: {ru_result}")
            print()

        except Exception as e:
            print(f"Error with MyMemory: {str(e)}")
            print()

        sleep(1)

    # Test Linguee Translator
    print("\nTesting with Linguee Translator:")
    print("-" * 50)
    for text in test_texts:
        try:
            en_result = LingueeTranslator(source='he', target='en').translate(text)
            print(f"Original: {text}")
            print(f"To English: {en_result}")

            ru_result = LingueeTranslator(source='he', target='ru').translate(text)
            print(f"To Russian: {ru_result}")
            print()

        except Exception as e:
            print(f"Error with Linguee: {str(e)}")
            print()

        sleep(1)

    # Test PONS Translator
    print("\nTesting with PONS Translator:")
    print("-" * 50)
    for text in test_texts:
        try:
            en_result = PonsTranslator(source='he', target='en').translate(text)
            print(f"Original: {text}")
            print(f"To English: {en_result}")

            ru_result = PonsTranslator(source='he', target='ru').translate(text)
            print(f"To Russian: {ru_result}")
            print()

        except Exception as e:
            print(f"Error with PONS: {str(e)}")
            print()

        sleep(1)


if __name__ == "__main__":
    test_translations()