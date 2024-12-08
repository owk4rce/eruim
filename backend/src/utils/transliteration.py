eng_to_ru = {
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


def transliterate_en_to_ru(text):
    # multi-letter combinations
    for seq, rus in {'ch': 'ч', 'Ch': 'Ч', 'CH': 'Ч',
                     'sh': 'ш', 'Sh': 'Ш', 'SH': 'Ш',
                     'th': 'т', 'Th': 'Т', 'TH': 'Т',
                     'ts': 'ц', 'Ts': 'Ц', 'TS': 'Ц'}.items():
        text = text.replace(seq, rus)

    # one by one
    transliterated = ''.join(eng_to_ru.get(char, char) for char in text)
    return transliterated


eng_to_hebrew = {
    'a': 'א',
    'b': 'ב',
    'c': 'ק',
    'd': 'ד',
    'e': 'א',
    'f': 'פ',
    'g': 'ג',
    'h': 'ה',
    'i': 'י',
    'j': 'ג',
    'k': 'ק',
    'l': 'ל',
    'm': 'מ',
    'n': 'נ',
    'o': 'ו',
    'p': 'פ',
    'q': 'ק',
    'r': 'ר',
    's': 'ס',
    't': 'ת',
    'u': 'ו',
    'v': 'ב',
    'w': 'ו',
    'x': 'קס',
    'y': 'י',
    'z': 'ז',
    'ch': 'ח',
    'sh': 'ש',
    'th': 'ת',
    'ts': 'צ'
}


def transliterate_en_to_he(text):
    # because hebrew is always lowercase
    text = text.lower()

    # multi-letter combinations
    for seq, heb in {'ch': 'ח', 'sh': 'ש', 'th': 'ת', 'ts': 'צ'}.items():
        text = text.replace(seq, heb)

    # one by one
    transliterated = ''.join(eng_to_hebrew.get(char, char) for char in text)
    return transliterated
