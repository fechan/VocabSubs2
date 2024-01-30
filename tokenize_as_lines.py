# Step 1: Tokenize subtitles
# given a text file with sentences, produce another text file with each line
# containing one token

import json
from japaneseanalyzer import JapaneseAnalyzer

import pykakasi
kks = pykakasi.kakasi()
kks.setMode("J", "H")
kks.setMode("s", True)
conv = kks.getConverter()

analyzer = JapaneseAnalyzer()

with open("nichibros-intro.txt") as f:
    lines = f.readlines()
    utterances_tokenized = []

    with open("nichibros-intro-tokens.txt", "w") as f:
        for utterance in lines:
            tokens = [{"token": token["token"], "meaning": token["def"]["meaning"]} for token in analyzer.tokenize(utterance)]

            for token in tokens:
                token["pron"] = kks.do(token["token"])

            utterances_tokenized.append(tokens)

            for token in tokens:
                f.write(token["token"] + "\n")
            f.write("\n")

    with open("nichibros-intro-defs.json", "w") as f:
        json.dump(utterances_tokenized, f, ensure_ascii=False, indent=2)