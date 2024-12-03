from hebrew import Hebrew



translator = Hebrew()
english_text = "Hello, World!"
hebrew_text = translator.translit(english_text)
print(hebrew_text)  # Output: שלום, עולם!