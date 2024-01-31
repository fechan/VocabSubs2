# Step 1: Tokenize subtitles
# given a text file with sentences, produce another text file with each line
# containing one token.
# Each utterance is separated by two newlines (\n\n)

import json
from japaneseanalyzer import JapaneseAnalyzer

import pykakasi
kks = pykakasi.kakasi()
kks.setMode("J", "H")
kks.setMode("s", True)
conv = kks.getConverter()

analyzer = JapaneseAnalyzer()

def tokenize_utterances(utterances: list[str]):
    utterances_tokenized = []
    tokens_hiragana = ""

    for utterance in utterances:
        tokens = [{"token": token["token"], "meaning": token["def"]["meaning"]} for token in analyzer.tokenize(utterance)]

        for token in tokens:
            token["pron"] = conv.do(token["token"])

        utterances_tokenized.append(tokens)

        for token in tokens:
            tokens_hiragana += token["pron"]

        tokens_hiragana += "\n"

    return utterances_tokenized, tokens_hiragana