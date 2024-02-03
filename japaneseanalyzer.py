from fugashi import Tagger
from jamdict import Jamdict
import re

PARTS_OF_SPEECH = {
    "助詞": "particle",
    "助動詞": "auxverb",
    "空白": "whitespace",
    "動詞": "verb",
    "名詞": "noun",
    "感動詞": "adjective",
    "補助記号": "punctuation",
}

class JapaneseAnalyzer:
    def __init__(self):
        self.tagger = Tagger("-Owakati")
        self.jmd = Jamdict()

        self.lemma_cache = {}

    def get_definition_string(self, entry, pos):
        sense = [sense for sense in entry.senses if pos in sense.pos[0]][0]
        definition = sense.gloss[0].text
        definition = re.sub("\s?\(.+\)\s?", "", definition)
        if pos == "verb":
            definition = re.sub("^to ", "", definition)
        definition = re.sub("\s+", ".", definition)
        return definition    

    def define_word(self, word):
        pos = PARTS_OF_SPEECH.get(word.feature.pos1, word.feature.pos1)
        if pos in ["particle", "whitespace", "auxverb", "punctuation"]:
            return {"lemma": word.feature.lemma, "pron": word.feature.pron, "meaning": word.surface}

        lemma = word.feature.lemma
        if lemma not in self.lemma_cache:
            try:
                definition = self.jmd.lookup_iter(lemma)

                entry = next(definition.entries)
                # def_text = "\n".join(('* ' + sense.gloss[0].text for sense in entry.senses))
                def_text = self.get_definition_string(entry, pos)
                self.lemma_cache[lemma] = {"lemma": lemma, "pron": str(entry.kana_forms[0]), "meaning": def_text}

            except (ValueError, IndexError, StopIteration):
                self.lemma_cache[lemma] = {"lemma": word.surface, "pron": word.feature.pron or "", "meaning": word.surface}
            
        return self.lemma_cache[lemma]

    def tokenize(self, text, define_tokens=True):
        tokens = []
        for word in self.tagger(text):
            lemma_def = self.define_word(word) if define_tokens else {"lemma": None, "pron": None, "meaning": None}
            tokens.append({
                "token": word.surface,
                "pron": word.feature.pron,
                "def": lemma_def
            })

        return tokens