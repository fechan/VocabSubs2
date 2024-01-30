# Step 2: Convert tokens to hiragana
# After this, Step 3 is running it through echogarden/Whisper
# Whisper has a limited Kanji vocabulary, so it's better to tokenize first
# then just have Whisper align each hiragana token to the audio

import pykakasi
kks = pykakasi.kakasi()
kks.setMode("J", "H")
kks.setMode("s", True)
with open("nichibros-intro-tokens.txt") as f:
    text = f.read()
    conv = kks.getConverter()
    result = conv.do(text)
    
    with open("nichibros-intro-tokens-hiragana.txt", "w") as f:
        f.write(result)