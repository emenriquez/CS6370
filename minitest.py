import json
import pandas as pd

def correlateDocuments(word_list='zhoogle/documents/fixtures/occurrences.json', doc_list='rhf_documents.json'):
    with open(word_list, 'r') as f:
        data = json.load(f)

    with open(doc_list, 'r') as f:
        documents = json.load(f)
    
    documents = list(documents.keys())

    data_df = pd.json_normalize(data)
    data_df.drop(['model', 'fields.freq', 'fields.locations'], axis=1, inplace=True)


    correlated_docs_final = {}
    counter = 0

    for doc1 in documents[:200]:
        document_correlations = {}
        doc_words = {}
        doc1_df = data_df[data_df['fields.doc_id'] == doc1]
        doc1_words = set(doc1_df['fields.word'].values)
        
        for doc2 in documents[:200]:
            doc2_words = {}
            doc2_df = data_df[data_df['fields.doc_id'] == doc2]

            new_df = doc1_df.merge(doc2_df, left_on='fields.word', right_on='fields.word')

            new_df['score'] = new_df['fields.tf_idf_x']*new_df['fields.tf_idf_y']
            correlation_score = new_df['score'].sum(axis=0)

            document_correlations[doc2] = correlation_score
        
        max_score = document_correlations[doc1]

        top_document_correlations = [(k, v/max_score) for k, v in sorted(document_correlations.items(), key=lambda item: item[1], reverse=True)][1:11]

        correlated_docs_final[doc1] = top_document_correlations

        counter += 1
        print(f"{counter}/{len(documents)} complete\r", end="")

    return correlated_docs_final

top_docs = correlateDocuments()

with open('rhf_doc_correlations.json', 'w') as f:
    json.dump(top_docs, f)

