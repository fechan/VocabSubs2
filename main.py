import uuid
import msgpack
from websockets.sync.client import connect

from preprocessor import preprocess_subs
from tokenizer import tokenize_utterances
from generate_karaoke_subs import make_karaoke

INPUT_FILE = "./nichibros/nichibros1.ass"
DO_FIRST_N_UTTERANCES = 16

subs_no_parens, utterances = preprocess_subs(INPUT_FILE)

utterances = utterances[:DO_FIRST_N_UTTERANCES]

utterances_tokenized, tokens_kanji, tokens_hiragana = tokenize_utterances(utterances)

with connect("ws://localhost:45054") as echogarden:
    alignment_request = {
        "messageType": "AlignmentRequest",
        "requestId": str(uuid.uuid4()),
        "input": "../nichibros/nichibros-intro-long.wav", # TODO: fix me
        "transcript": tokens_kanji,
        "options": {
            "engine": "whisper",
            "language": "ja",
            "whisper": {
                "model": "tiny",
            },
            "plainText": {
                "paragraphBreaks": "double",
            }
        }
    }
    echogarden.send(msgpack.packb(alignment_request))
    response = msgpack.unpackb(echogarden.recv())

karaoke_sub_track = make_karaoke(utterances_tokenized, response["timeline"])
karaoke_sub_track.save("./nichibros1.kar.ass")