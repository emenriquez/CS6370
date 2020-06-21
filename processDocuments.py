import json

# Read Documents dictionary and convert it into format compatible with Django import
with open('rhf_documents.json', 'r') as f:
    documents = json.load(f)

processed_docs = []
for doc in documents.keys():
    new_doc = {
        'model': 'documents.document',
        'pk': doc,
        'fields': documents[doc]
    }
    processed_docs.append(new_doc)

with open('zhoogle/documents/fixtures/documents.json', 'w') as f:
    json.dump(processed_docs, f)

# Read Corpus dictionary and convert it into format compatible with Django import
with open('rhf_corpus.json', 'r') as f:
    corpus = json.load(f)

processed_words = []
processed_occurrences = []
for word in corpus.keys():
    new_word = {
        'model': 'documents.word',
        'pk': word,
        'fields': {
            'df': corpus[word]['df']
        }
    }
    for hits in corpus[word]['occurrences']:
        new_occurrence = {
            'model': 'documents.occurrence',
            'fields': {
                'word': word,
                'doc_id': hits['doc_id'],
                'freq': hits['freq'],
                'tf_idf': hits['tf_idf'],
                'locations': hits['locations'],
            }
        }

        processed_occurrences.append(new_occurrence)
        
    processed_words.append(new_word)
    

with open('zhoogle/documents/fixtures/words.json', 'w') as f:
    json.dump(processed_words, f)

with open('zhoogle/documents/fixtures/occurrences.json', 'w') as f:
    json.dump(processed_occurrences, f)