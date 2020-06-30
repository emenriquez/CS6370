import json
import pandas as pd

def correlateKeywords(word_list='zhoogle/documents/fixtures/occurrences.json'):
    '''
    **Very similar to above function "correlateDocuments" in structure**

    This function will take in the list of word occurrences in the corpus and use it to correlate documents.
    The correlation is done by computing the inner product of tf_idf values between 1 document and the corpus, and the script will return entries for the top 5 correlated documents.
    The output is formatted for loading into Django as a fixture.
    '''
    with open(word_list, 'r') as f:
        data = json.load(f)

    # dataframe was employed since it is much faster for filtering and getting cartesian products of document data
    data_df = pd.json_normalize(data)
    data_df.drop(['model', 'fields.freq', 'fields.locations'], axis=1, inplace=True)
    data_df.rename(columns={'fields.word': 'word', 'fields.doc_id': 'doc_id', 'fields.tf_idf': 'tf_idf'}, inplace=True)

    words = data_df.word.unique()


    processed_keywords = []
    counter = 0

    for word in words:
        word1_df = data_df[data_df['word'] == word]
        
        final_df = word1_df.merge(data_df, on='doc_id')

        final_df['score'] = final_df['tf_idf_x']*final_df['tf_idf_y']

        final_df = final_df.groupby('word_y').sum().sort_values(by='score', ascending=False)

        final_df['score'] = final_df['score']/final_df['score'].max()

        # Loop through the top 5 results. Range can be changed to top X results
        # item with index 0 is excluded since this is always the top score, where the document is perfectly correlated with itself
        for i in range(1, 6):
            new_word = {
            'model': 'documents.keyword',
            'fields': {
                'word': word,
                'keyword': final_df.index[i],
                'score': final_df.iloc[i]['score'],
            }
            }

            processed_keywords.append(new_word)

        # Update user since this will take a little while...
        counter += 1
        print(f" Progress: {counter}/{len(words)} complete\r", end="")

    return processed_keywords

keywords = correlateKeywords()

with open('keywords.json', 'w') as f:
    json.dump(keywords, f)