# Step 1: Tokenize subtitles
# given a text file with sentences, produce another text file with each line
# containing one token.
# Each utterance is separated by two newlines (\n\n)

import json
from japaneseanalyzer import JapaneseAnalyzer

import pykakasi
kks = pykakasi.kakasi()
kks.setMode("J", "H")
kks.setMode("K", "H")
kks.setMode("s", True)
conv = kks.getConverter()

analyzer = JapaneseAnalyzer()

def tokenize_utterances(utterances: list[str]) -> (list[list[dict]], str, str):
    utterances_tokenized = []
    tokens_hiragana = ""
    tokens_kanji = ""

    for utterance in utterances:
        tokens_hiragana += "<s>"
        tokens_kanji += "<s>"
        tokens = [{"token": token["token"], "meaning": (token["def"]["meaning"] or token["token"])} for token in analyzer.tokenize(utterance)]

        for token in tokens:
            token["pron"] = conv.do(token["token"])

        utterances_tokenized.append(tokens)

        for token in tokens:
            tokens_hiragana += token["pron"] + "\n"
            tokens_kanji += token["token"] + "\n"

        tokens_hiragana += "</s>"
        tokens_kanji += "</s>"

    return utterances_tokenized, tokens_kanji, tokens_hiragana