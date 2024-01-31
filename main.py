from preprocessor import preprocess_subs
from tokenizer import tokenize_utterances

INPUT_FILE = "./nichibros/nichibros1.ass"
DO_FIRST_N_UTTERANCES = 20

subs_no_parens, utterances = preprocess_subs(INPUT_FILE)

utterances = utterances[:DO_FIRST_N_UTTERANCES]

utterances_tokenized, tokens_hiragana = tokenize_utterances(utterances)