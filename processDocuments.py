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



def reduceVocabulary(word_json='rhf_corpus.json', min_frequency=5, max_frequency=5000):
    '''
    This function takes in a full list of search terms and drastically reduces the size by removing words with low frequency.
    Cutoff frequency can be set by the min_frequency input value.
    Returns a dictionary with reduced size.
    '''
    with open(word_json, 'r') as f:
        data = json.load(f)
    
    unwanted_words = []

    for word in data.keys():
        if data[word]['df'] < min_frequency or data[word]['df'] > max_frequency:
            unwanted_words.append(word)
    
    for word in unwanted_words:
        data.pop(word)

    return data

# Read Corpus dictionary and reduce the dictionary size by removing words that occur less than 5 times (to increase speed)
corpus = reduceVocabulary('rhf_corpus.json', min_frequency=5, max_frequency=10000)

# convert reduced vocabulary into format compatible with Django import
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