import json

def reduceVocabulary(word_list='rhf_corpus.json'):
    with open(word_list, 'r') as f:
        data = json.load(f)
    
    unwanted_words = []

    for word in data.keys():
        if data[word]['df'] > 5000 or data[word]['df'] < 5:
            unwanted_words.append(word)
    
    for word in unwanted_words:
        data.pop(word)

    return data

new_list = reduceVocabulary('rhf_corpus.json')
print(len(new_list))