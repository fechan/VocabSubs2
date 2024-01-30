# Final step for recombining all data steams into output subs

import json
import pysubs2

START_OF_AUDIO_OFFSET = 8

# whisper token timings feel a little slow, so we show each token a little earlier to compensate
TOKEN_TIMING_OFFSET = -0.25

with open("nichibros-intro-defs.json", "r") as f:
    real_segments = json.load(f)

with open("nichibros-intro-fullsent.json", "r") as f:
    whisper_segments = json.load(f)

in_sub_track = pysubs2.SSAFile.load("nichibros1.ass")
out_sub_track = pysubs2.SSAFile()

def get_karaoke_for_segment(segment):
    """ Once the tokens in real_segments have been timed, pass them here to generate
        the Karaoke text for them
    """
    out = ""

    for token in segment:
        # Karaoke duration is formatted in centiseconds (see https://aegisub.org/docs/latest/ass_tags/)
        duration = int(100 * (token["endTime"] - token["startTime"]))
        out += "{\k" + str(duration) + "}" + token["meaning"] + " "

    return out

for segment_no, real_segment in enumerate(real_segments):
    print("\nreal |", " ".join([token["pron"] for token in real_segment]))
    whisper_segment = whisper_segments[segment_no]

    whisper_words = []
    for sentence in whisper_segment["timeline"]:
        print("whis |", " ".join([word["text"] for word in sentence["timeline"]]))
        whisper_words += sentence["timeline"]

    for token_no, token in enumerate(real_segment):
        corresponding_whisper_words = []

        if (len(whisper_words) == 0) or (not token["pron"].startswith(whisper_words[0]["text"])):
            # the next whisper word has nothing to do with the current real token,
            # so the current real token might be punctuation or something and
            # cannot be timed
            print("Ignoring token", token["token"], "because it could not be timed")
            continue

        def concat_whisper_words(words):
            return "".join([word["text"] for word in words])

        first_token = True # is this the first whisper word we've checked for correspondence with the current real token?
        while token["pron"] != concat_whisper_words(corresponding_whisper_words):
            if len(whisper_words) == 0: break
            corresponding_whisper_words.append(whisper_words.pop(0))
            first_token = False

        token["startTime"] = corresponding_whisper_words[0]["startTime"]
        token["endTime"] = corresponding_whisper_words[-1]["endTime"]
        
    timed_tokens = [token for token in real_segment if "startTime" in token]
    start_time = pysubs2.make_time(s = START_OF_AUDIO_OFFSET + timed_tokens[0]["startTime"] + TOKEN_TIMING_OFFSET)
    end_time = pysubs2.make_time(s = START_OF_AUDIO_OFFSET + timed_tokens[-1]["endTime"] + TOKEN_TIMING_OFFSET)
    text = get_karaoke_for_segment(timed_tokens)

    out_sub_track.events.append(pysubs2.SSAEvent(start=start_time, end=end_time, effect="karaoke", text=text))

out_sub_track.save("nichibros1.kef.ass")