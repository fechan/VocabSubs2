import urllib.request, urllib.parse
import json

ENDPOINT = "https://jisho.org/api/v1/search/words?keyword="

def get_jisho_def(word):
    word_parsed = urllib.parse.quote(word)
    with urllib.request.urlopen(ENDPOINT + word_parsed) as response:
        data = json.load(response)

        try:
            return {
                "lemma": data["data"][0]["japanese"][0]["word"],
                "pron": data["data"][0]["japanese"][0]["reading"],
                "meaning": data["data"][0]["senses"][0]["english_definitions"][0],
                "pos": data["data"][0]["senses"][0]["parts_of_speech"][0]
            }
        except (IndexError, KeyError):
            return None