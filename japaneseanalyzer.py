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
    "補助記号": "punctuation",
}

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

    def define_word(self, word):
        pos = PARTS_OF_SPEECH.get(word.feature.pos1, word.feature.pos1)
        if pos in ["particle", "whitespace", "auxverb", "punctuation"]:
            return {"lemma": word.feature.lemma, "meaning": word.surface}

        lemma = word.feature.lemma
        if lemma not in self.lemma_cache:
            if re.match("^[ァ-ン]+$", word.surface): # if it's all katakana, jamdict has issues lemmatizing it
                jisho_result = get_jisho_def(word.surface) if USE_JISHO else None
                if jisho_result != None:
                    jisho_result["meaning"] = self.get_definition_string(jisho_result["meaning"], jisho_result["pos"])
                    self.lemma_cache[lemma] = jisho_result
                    return jisho_result
                else:
                    return {"lemma": word.surface, "meaning": word.surface}

            try:
                definition = self.jmd.lookup_iter(lemma)

                entry = next(definition.entries)
                # def_text = "\n".join(('* ' + sense.gloss[0].text for sense in entry.senses))
                sense = [sense for sense in entry.senses if pos in sense.pos[0]][0]
                definition = sense.gloss[0].text
                def_text = self.get_definition_string(definition, pos)
                self.lemma_cache[lemma] = {"lemma": lemma, "meaning": def_text}

            except (ValueError, IndexError, StopIteration):
                if re.match("([^ぁ-んァ-ンA-z])", word.surface):
                    jisho_result = get_jisho_def(word.surface) if USE_JISHO else None
                    if jisho_result != None:
                        jisho_result["meaning"] = self.get_definition_string(jisho_result["meaning"], jisho_result["pos"])
                        self.lemma_cache[lemma] = jisho_result

                if lemma not in self.lemma_cache:
                    self.lemma_cache[lemma] = {"lemma": word.surface, "meaning": word.surface}
            
        return self.lemma_cache[lemma]

    def tokenize(self, text, define_tokens=True):
        tokens = []
        for word in self.tagger(text):
            lemma_def = self.define_word(word) if define_tokens else {"lemma": None, "meaning": None}
            tokens.append({
                "token": word.surface,
                "def": lemma_def
            })

        return tokens