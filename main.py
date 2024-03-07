import ffmpeg
import os
import shutil
import itertools
from preprocessor import preprocess_subs
from tokenizer import tokenize_utterances
from generate_karaoke_subs import make_karaoke

INPUT_AUDIO = "./nichibros/nichibros1.mkv"
INPUT_FILE = "./nichibros/nichibros1.ass"
CLIPS_DIR = "./nichibros/clips/"
WRITE_CLIPS = True # You can set this to False iff you've already generated audio clips before
DEVICE = "cuda"
DO_FIRST_N_UTTERANCES = 25

if WRITE_CLIPS:
    shutil.rmtree(CLIPS_DIR)
    os.mkdir(CLIPS_DIR)

subs_no_parens, utterances = preprocess_subs(INPUT_FILE)

# cut up audio according to subs_no_parens
def make_clip(subtitles, out_clip_path, current_clip_start, current_clip_end):
    current_clip_length = current_clip_end - current_clip_start
    if WRITE_CLIPS:
        (audio.filter("atrim", start=current_clip_start/1000, duration=current_clip_length/1000)
            .output(out_clip_path)
            .run()
        )
    tokens, tokens_kanji, tokens_hiragana = tokenize_utterances(subtitles)
    return {
        "path": out_clip_path,
        "start": current_clip_start,
        "duration": current_clip_length,
        "tokens": tokens,
        "kanji": tokens_kanji,
    }

max_clip_length = 29 * 1000 # in milliseconds. whisperx only supports sub-30 second clips

clips = []
current_clip_sub_texts = []
current_clip_start = subs_no_parens[0].start # in milliseconds
current_clip_end = subs_no_parens[0].end

audio = ffmpeg.input(INPUT_AUDIO).audio

for sub_num, subtitle in enumerate(subs_no_parens[:min(DO_FIRST_N_UTTERANCES, len(subs_no_parens))]):
    out_clip_path = CLIPS_DIR + str(current_clip_start) + ".wav"
    if subtitle.end - current_clip_start > max_clip_length:
        clips.append(make_clip(current_clip_sub_texts, out_clip_path, current_clip_start, current_clip_end))
        
        current_clip_sub_texts = [subtitle.text]
        current_clip_start = subtitle.start
    else:
        current_clip_sub_texts.append(subtitle.text)
    current_clip_end = subtitle.end
        
clips.append(make_clip(current_clip_sub_texts, out_clip_path, current_clip_start, current_clip_end))

import whisperx
align_model, metadata = whisperx.load_align_model(language_code="ja", device=DEVICE)

def offset_whisper_segments(whisper_segments, offset_s):
    for segment in whisper_segments:
        if "start" in segment:
            segment["start"] += offset_s
            segment["end"] += offset_s

        for word in segment["words"]:
            if "start" in word:
                word["start"] += offset_s
                word["end"] += offset_s

whisper_segments = []
utterances_tokenized = []

for clip in clips:
    utterances_tokenized += clip["tokens"]
    audio_path = clip["path"]
    transcription = [{"text": clip["kanji"], "start": 0.0, "end": clip["duration"]/1000}]

    aligned = whisperx.align(transcription, align_model, metadata, audio_path, DEVICE)

    offset_whisper_segments(aligned["segments"], clip["start"]/1000)

    new_whisper_segments = []
    groups = itertools.groupby(aligned["segments"][0]["words"], (lambda v: ("start" not in v) and (v["word"] in ["<", "/", "s", ">"])))

    for is_delimiter, g in groups:
        if not is_delimiter:
            new_whisper_segments.append(list(g))

    whisper_segments += new_whisper_segments

karaoke_sub_track = make_karaoke(utterances_tokenized, whisper_segments)
karaoke_sub_track.save("./nichibros/nichibros1.kar.ass")