# Final step for recombining all data steams into output subs

import json
import pysubs2

START_OF_AUDIO_OFFSET = 0

# whisper token timings feel a little slow, so we show each token a little earlier to compensate
TOKEN_TIMING_OFFSET = -0.25

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

def concat_whisper_words(words):
    return "".join([word["word"] for word in words])

def make_karaoke(real_segments: list[list[dict]], whisper_segments):
    out_sub_track = pysubs2.SSAFile()

    for segment_no, real_segment in enumerate(real_segments):
        print("\nreal |", " ".join([token["token"] for token in real_segment]))
        if segment_no == len(whisper_segments):
            break # TODO: actually figure out why this happens. I think it's because the last audio clip being generated is incorrectly leaving out the last sub
        whisper_segment = whisper_segments[segment_no]

        whisper_words = [word for word in whisper_segment if "start" in word] # "start" will only appear in word if it's an actual word and not punctuation
        print("whis |", " ".join([word["word"] for word in whisper_segment]))

        for token_no, token in enumerate(real_segment):
            corresponding_whisper_words = []

            if (len(whisper_words) == 0) or (not token["token"].startswith(whisper_words[0]["word"])):
                # the next whisper word has nothing to do with the current real token,
                # so the current real token might be punctuation or something and
                # cannot be timed
                if token_no - 1 >= 0:
                    real_segment[token_no - 1]["meaning"] += token["token"]
                print("Concatenating", token["token"], "with previous token because it could not be timed")
                continue

            while token["token"] != concat_whisper_words(corresponding_whisper_words):
                if len(whisper_words) == 0: break
                corresponding_whisper_words.append(whisper_words.pop(0))

            token["startTime"] = corresponding_whisper_words[0]["start"]
            token["endTime"] = corresponding_whisper_words[-1]["end"]
            
        timed_tokens = [token for token in real_segment if "startTime" in token]
        try:
            start_time = pysubs2.make_time(s = START_OF_AUDIO_OFFSET + timed_tokens[0]["startTime"] + TOKEN_TIMING_OFFSET)
            end_time = pysubs2.make_time(s = START_OF_AUDIO_OFFSET + timed_tokens[-1]["endTime"] + TOKEN_TIMING_OFFSET)
            text = get_karaoke_for_segment(timed_tokens)

            out_sub_track.events.append(pysubs2.SSAEvent(start=start_time, end=end_time, effect="karaoke", text=text))
            print("subs |", text)
        except:
            print("Unable to make karaoke subtitle for this segment!")


    return out_sub_track