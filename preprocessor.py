# Step 0: Remove parentheses from raw subs and replace \N with \n
#
# - Parentheses usually indicate speaker tags which are not actually spoken
#   verbally
# - \N creates a line break in the same subtitle, but for simplicity we'll treat
#   each line as a separate utterance

import pysubs2
import re
import os.path as path

def preprocess_subs(subtitle_path: str):
    subs = pysubs2.load(subtitle_path, encoding="utf-8")
    utterances = []

    for line in subs:
        line.text = re.sub(r"[\(\（].+[\)\）]\s?", "", line.text) # remove parentheticals
        utterances += line.text.strip().replace("\\N", "\n").split("\n")
    
    utterances = [u for u in utterances if len(u) > 0]

    return subs, utterances