from bs4 import BeautifulSoup
from zipfile import ZipFile

import math
import json

# List of stop words to remove as preprocessing, this word list was sourced from https://gist.github.com/sebleier/554280
stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]

def buildHashMap(zipped_folder):
    '''
    This function will take in a zipped folder of html pages and iterate through them, extracting all words from the pre-processed html text.
    It will output a dictionary of words occuring the collection of pages.
    The dictionary keys are words that contain a list of occurrences and locations of where the terms are found in the documents.
    '''
    with ZipFile(zipped_folder, 'r') as zip:
        # Display the directory of files in the zip folder
        # zip.printdir()
        word_list = {}
        document_list = {}
        counter = 0

        # Loop through each file in the zip container
        for name in zip.namelist():
            # Read the html file
            data = zip.read(name)

            # Parse the data with BeautifulSoup
            soup = BeautifulSoup(data, 'html.parser')

            # Extract the text from the html file and generate a list of "words" separated by spaces
            page_text = soup.getText().split()

            # Add document to document_list
            document_list[name] = {
                'vector_length': 0,
                'max_freq': 0,
                }

            # Loop through words in extracted text and preprocess to exclude prohibited words
            doc_words = {}
            for id, word in enumerate(page_text):

                # Check if word contains only letters
                if word.isalpha() and word.lower() not in stop_words:
                    counter += 1
                    # set word to lowercase
                    word = word.lower()

                    # Map frequencies and occurrences for each word in the corpus
                    if word in doc_words.keys():
                        doc_words[word]['freq'] += 1
                        doc_words[word]['locations'].append(id)
                    else:
                        doc_words[word] = {
                            'doc_id': name,
                            'freq': 1,
                            'tf_idf': 0,
                            'locations': [id]
                        }
            # Add document words to corpus vocabulary
            for word in doc_words.keys():
                # Check word frequency and Add new max_freq to document list
                max_freq = max(doc_words[word]['freq'], document_list[name]['max_freq'])
                document_list[name]['max_freq'] = max_freq
                
                if word in word_list.keys():
                    word_list[word]['df'] += 1
                    word_list[word]['occurrences'].append(doc_words[word])
                else:
                    word_list[word] = {
                        'df': 1,
                        'occurrences': [doc_words[word]],
                    }

            doc_words = {}
    
    num_documents = len(document_list.keys())

    for word in word_list.keys():
        for id, hit in enumerate(word_list[word]['occurrences']):
            # Calculate and update the tf-idf score of each word
            doc = hit['doc_id']
            max_freq = document_list[doc]['max_freq']
            word_freq = hit['freq']
            tf = word_freq / max_freq
            df = word_list[word]['df'] + 1
            idf = math.log2(num_documents / df) + 1
            tf_idf = tf*idf
            word_list[word]['occurrences'][id]['tf_idf'] = tf_idf
            document_list[doc]['vector_length'] += (tf_idf*tf_idf)
    
    # Take square root of each document vector length, since it was not done in previous loop
    for doc in document_list.keys():
        old_length = document_list[doc]['vector_length']
        document_list[doc]['vector_length'] = math.sqrt(old_length)
    
    print(counter)
    return word_list, document_list

def runSearch(corpus):
    '''
    The following function takes in user input and searches a hashed map of vocabulary built from a corpus of html web pages.
    The search will return all documents where the term occurred.
    The search will terminate when the user input is empty.
    '''
    print('Beginning Search. Press Enter with no search term to exit at any time.')
    running = True
    
    while running:
        # Request user input
        res = input('enter a search key=> ')
        if res == '':
            print('Ending Search. Bye!')
            running = False
        # Error handling for non-words or special character terms (they don't appear in the vocabulary)
        elif not res.isalpha():
            print('Your search term must be a word! No special characters or numbers, please.')
        else:
            try:
                hits = corpus[res]['occurrences']
                print("Found a match in the following pages: ")
                [print(hit['doc_id']) for hit in hits]
            except KeyError:
                print('Your search returned no results')


corpus, documents = buildHashMap('Jan.zip')
# runSearch(corpus)

with open('corpus.json', 'w') as f:
    json.dump(corpus, f)

with open('documents.json', 'w') as f:
    json.dump(documents, f)