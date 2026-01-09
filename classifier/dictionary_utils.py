import os

WORD_GLOSS = {}
WORD_LEVEL = {}

def load_cleaned_kengdic():
    global WORD_GLOSS, WORD_LEVEL
    if WORD_GLOSS:
        return  # already loaded

    file_path = os.path.join(os.path.dirname(__file__), 'kengdic_cleaned.tsv')

    with open(file_path, encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 4:
                continue
            _id, word, gloss, level = parts
            WORD_GLOSS[word] = gloss
            if level.strip():  # only store level if prese
                                WORD_LEVEL[word] = level.strip().upper()

KOREAN_DICTIONARY = load_cleaned_kengdic()

def get_meaning(word):
    return KOREAN_DICTIONARY.get(word)
