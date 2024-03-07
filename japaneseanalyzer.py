import re
# from fugashi import Tagger
import nagisa
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
    "名詞": "name",
    "接尾辞": "suffix",
    "副詞": "adverb",
}

USE_JISHO = False

class JapaneseAnalyzer:
    def __init__(self):
        self.tagger = nagisa.tagging
        self.jmd = Jamdict()

        self.lemma_cache = {}

    def get_definition_string(self, definition, pos):
        definition = re.sub("\s?\(.+\)\s?", " ", definition)
        if "verb" in pos:
            definition = re.sub("^to ", "", definition)
        definition = re.sub("\s+", ".", definition.strip())
        return definition

    def define_word(self, word, word_pos_ja):
        lemma = word
        surface_form = word

        pos = PARTS_OF_SPEECH.get(word_pos_ja, word_pos_ja)
        if pos in ["particle", "whitespace", "auxverb", "punctuation"]:
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
                entry = next(definition.entries)
                
                # if possible, try to match the part of speech returned by the tokenizer
                possible_senses = [sense for sense in entry.senses if pos in sense.pos[0]]
                if len(possible_senses) == 0:
                    possible_senses = entry.senses
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
        for word_idx, word in enumerate(tagged_text.words):
            if re.match("^\s+$", word):
                continue

            if define_tokens:
                word_pos = tagged_text.postags[word_idx]
                lemma_def = self.define_word(word, word_pos)
            else:
                lemma_def = {
                    "lemma": None,
                    "meaning": None
                }

            tokens.append({
                "token": word,
                "def": lemma_def
            })

        return tokens