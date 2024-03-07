import re
from fugashi import Tagger
from jamdict import Jamdict
from jisho import get_jisho_def

PARTS_OF_SPEECH = {
    "助詞": "particle",
    "助動詞": "auxverb",
    "空白": "whitespace",
    "動詞": "verb",
    "名詞": "noun",
    "感動詞": "adjective",
    "形容詞": "adjective",
    "補助記号": "punctuation",
    "接尾辞": "suffix",
    "副詞": "adverb",
    "代名詞": "pronoun",
}

UNTRANSLATED_WORDS = [
    "particle",
    "whitespace",
    "auxverb",
    "punctuation",
    "suffix",
]

USE_JISHO = False

class JapaneseAnalyzer:
    def __init__(self):
        self.tagger = Tagger("-Owakati")
        self.jmd = Jamdict()

        self.lemma_cache = {}

    def get_definition_string(self, definition, pos):
        definition = re.sub("\s?\(.+\)\s?", " ", definition)
        if "verb" in pos:
            definition = re.sub("^to ", "", definition)
        definition = re.sub("\s+", ".", definition.strip())
        return definition

    def define_word(self, word, word_pos_ja):
        lemma = word.feature.lemma
        surface_form = word.surface

        pos = PARTS_OF_SPEECH.get(word_pos_ja, word_pos_ja)
        if pos in UNTRANSLATED_WORDS:
            return {"lemma": lemma, "meaning": surface_form}

        if lemma not in self.lemma_cache:
            if re.match("^[ァ-ン]+$", surface_form): # if it's all katakana, jamdict has issues lemmatizing it
                jisho_result = get_jisho_def(surface_form) if USE_JISHO else None
                if jisho_result != None:
                    jisho_result["meaning"] = self.get_definition_string(jisho_result["meaning"], jisho_result["pos"])
                    self.lemma_cache[lemma] = jisho_result
                    return jisho_result
                else:
                    self.lemma_cache[lemma] = {"lemma": surface_form, "meaning": surface_form}

            try:
                definition = self.jmd.lookup_iter(lemma)

                possible_senses = []
                for entry in definition.entries:
                    for sense in entry.senses:
                        for sense_pos in sense.pos:
                            if pos in sense_pos:
                                possible_senses.append(sense)
                sense = possible_senses[0]

                definition = sense.gloss[0].text
                def_text = self.get_definition_string(definition, pos)
                self.lemma_cache[lemma] = {"lemma": lemma, "meaning": def_text}

            except (ValueError, IndexError, StopIteration):
                if re.match("([^ぁ-んァ-ンA-z])", surface_form):
                    jisho_result = get_jisho_def(surface_form) if USE_JISHO else None
                    if jisho_result != None:
                        jisho_result["meaning"] = self.get_definition_string(jisho_result["meaning"], jisho_result["pos"])
                        self.lemma_cache[lemma] = jisho_result

                if lemma not in self.lemma_cache:
                    self.lemma_cache[lemma] = {"lemma": surface_form, "meaning": surface_form}
            
        return self.lemma_cache[lemma]

    def tokenize(self, text, define_tokens=True):
        tokens = []

        tagged_text = self.tagger(text)
        for word_idx, word in enumerate(tagged_text):
            # if re.match("^\s+$", word):
                # continue

            if define_tokens:
                word_pos = word.feature.pos1
                lemma_def = self.define_word(word, word_pos)
            else:
                lemma_def = {
                    "lemma": None,
                    "meaning": None
                }

            tokens.append({
                "token": word.surface,
                "def": lemma_def
            })

        return tokens