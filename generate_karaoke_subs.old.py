# (OLD) Final step for recombining all data steams into output subs

import json
import pysubs2

START_OF_AUDIO_OFFSET = 8

with open("nichibros-intro-defs.json", "r") as f:
    utterances_tokenized = json.load(f)

with open("nichibros-intro.json", "r") as f:
    whisper_tokens = json.load(f)

in_sub_track = pysubs2.SSAFile.load("nichibros1.ass")
out_sub_track = pysubs2.SSAFile()

cur_whisper_token = None

for utterance_idx, utterance in enumerate(utterances_tokenized):
    in_sub = in_sub_track.events[utterance_idx] # original subtitle event for the current utterance

    # Process first token
    cur_whisper_token = whisper_tokens.pop(0)
    cur_utterance_token = utterance.pop(0)

    while cur_utterance_token["pron"] != cur_whisper_token["text"]: # consume defined tokens until it matches with whisper tokens
        cur_utterance_token = utterance.pop()

    # whisper_start = pysubs2.make_time(s=cur_whisper_token["startTime"]-0.25)
    in_sub_start = in_sub.start - pysubs2.make_time(s=START_OF_AUDIO_OFFSET)
    whisper_end = pysubs2.make_time(s=cur_whisper_token["endTime"]-0.26)
    out_last_sub = pysubs2.SSAEvent(start=in_sub_start, end=whisper_end, text=cur_utterance_token["meaning"])
    
    print(out_last_sub.text)
    out_sub_track.events.append(out_last_sub)

    # Process rest of the tokens
    while len(utterance) > 0:
        out_last_sub = out_last_sub.copy()

        cur_whisper_token = whisper_tokens.pop(0)
        cur_utterance_token = utterance.pop(0)

        while cur_utterance_token["pron"] != cur_whisper_token["text"]: # consume defined tokens until it matches with whisper tokens
            if len(utterance) == 0: break
            cur_utterance_token = utterance.pop(0)

        out_last_sub.text += " " + (cur_utterance_token["meaning"] or cur_utterance_token["token"])
        out_last_sub.start = pysubs2.make_time(s=cur_whisper_token["startTime"]-0.25)
        out_last_sub.end = pysubs2.make_time(s=cur_whisper_token["endTime"]-0.26)

        print(out_last_sub.text)
        out_sub_track.events.append(out_last_sub)

out_sub_track.save("nichibros-intro.def.ass")