from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

# loading raw data
p_ids = ["PA", "PB", "PC", "PE", "PF", "PG", "PH", "PJ", "PK", "PM", "PN", "PO", "PI"]
raw_data = {}
for p_id in p_ids:
    with open("../data/transcripts/{}/{}.txt".format(p_id, p_id), "r") as infile:
        raw_data[p_id] = infile.read()

def chunk(p_id, p_sn):
    """
    turn interview transcript into list
    of chunks
    """
    chunks = raw_data[p_id].split('\n')
    chunks = [x for x in chunks if len(x) >= 10]
    chunks = [x[10::] for x in chunks if x[8] == str(p_sn) ]
    return '\n'.join(chunks)

def gc_sentiment(p_id, text):  
    client = language.LanguageServiceClient()
    document = language.types.Document(
    content=text,
    type=language.enums.Document.Type.PLAIN_TEXT)
    annotations = client.analyze_sentiment(document=document)

    # get overall sentiment score and magnitude for document
    score = annotations.document_sentiment.score
    magnitude = annotations.document_sentiment.magnitude

    # get sentiment score for each sentence
    sentence_sentiments = []
    for index, sentence in enumerate(annotations.sentences):
        sentence_sentiments.append((sentence.sentiment.score,
            sentence.sentiment.magnitude))

    # put results in a dict
    result = { "p_id": p_id, "score": score, "magnitude": magnitude,
            "sentence_scores": sentence_sentiments }
    return result

data = chunk('PO', 1)
result = gc_sentiment('PO', data)

import pickle
with open('../data/sentiment/PO', 'wb') as outfile:
    pickle.dump(result, outfile)
