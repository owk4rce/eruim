eng_to_russian = {
    'a': 'а', 'A': 'А',
    'b': 'б', 'B': 'Б',
    'c': 'к', 'C': 'К',
    'd': 'д', 'D': 'Д',
    'e': 'е', 'E': 'Е',
    'f': 'ф', 'F': 'Ф',
    'g': 'г', 'G': 'Г',
    'h': 'х', 'H': 'Х',
    'i': 'и', 'I': 'И',
    'j': 'й', 'J': 'Й',
    'k': 'к', 'K': 'К',
    'l': 'л', 'L': 'Л',
    'm': 'м', 'M': 'М',
    'n': 'н', 'N': 'Н',
    'o': 'о', 'O': 'О',
    'p': 'п', 'P': 'П',
    'q': 'к', 'Q': 'К',
    'r': 'р', 'R': 'Р',
    's': 'с', 'S': 'С',
    't': 'т', 'T': 'Т',
    'u': 'у', 'U': 'У',
    'v': 'в', 'V': 'В',
    'w': 'в', 'W': 'В',
    'x': 'кс', 'X': 'Кс',
    'y': 'й', 'Y': 'Й',
    'z': 'з', 'Z': 'З',
    'ch': 'ч', 'Ch': 'Ч', 'CH': 'Ч',
    'sh': 'ш', 'Sh': 'Ш', 'SH': 'Ш',
    'th': 'т', 'Th': 'Т', 'TH': 'Т',
    'ts': 'ц', 'Ts': 'Ц', 'TS': 'Ц'
}

def transliterate_to_russian(text):
    # Обрабатываем многобуквенные сочетания
    for seq, rus in {'ch': 'ч', 'Ch': 'Ч', 'CH': 'Ч',
                     'sh': 'ш', 'Sh': 'Ш', 'SH': 'Ш',
                     'th': 'т', 'Th': 'Т', 'TH': 'Т',
                     'ts': 'ц', 'Ts': 'Ц', 'TS': 'Ц'}.items():
        text = text.replace(seq, rus)

    # Транслитерируем посимвольно
    transliterated = ''.join(eng_to_russian.get(char, char) for char in text)
    return transliterated

# Пример использования
english_text = "ANU"
russian_text = transliterate_to_russian(english_text)
print(russian_text)  # Хелло Ворлд! Чанге ис гуд.