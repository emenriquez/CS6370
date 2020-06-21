import json

with open('rhf_corpus.json', 'r') as f:
    data = json.load(f)

counter = 0

for word in data.keys():
    # if data[word]['df'] < 5:
        counter += 1

print(counter)