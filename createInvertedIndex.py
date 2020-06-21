import json
from bs4 import BeautifulSoup
import math

# List of stop words to remove as preprocessing, this word list was sourced from https://gist.github.com/sebleier/554280
stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]

def getSnippetfromHTML(html_file):
    '''
    This function will take in an html file and generate a snippet to make searches prettier and a little more google-y.
    It is somewhat tailored to the html files in the RHF folder, but it should be able to handle general files with the last "else" statement
    It will return a snippet of the site contents as a string.
    '''
    # Parse the data with BeautifulSoup
    soup = BeautifulSoup(html_file, 'html.parser')

    if soup('pre'):
        snippet = soup('pre')[0].getText()[:100] + '...'
    elif '</PRE>' in html_file:
        start_snippet = html_file.find('</PRE>')
        snippet = BeautifulSoup(html_file[start_snippet:start_snippet + 100], 'html.parser').getText() + '...'
    elif soup('p'):
        # Take out the title so that it's not repeated in the snippet since it will be in the link above it
        if soup('title'):
            soup.find('title').extract()

        snippet_list = soup.getText().split()[:25]
        snippet = [word for word in snippet_list if word.isalpha()]
        snippet = ' '.join(snippet).replace("RHF Joke Archives ", "") + '...'
    else:
        snippet = soup.getText()[:100] + '...'

    snippet = ' '.join(snippet.split())
    
    return snippet

def buildHashMap(list_of_pages):
    '''
    This function will take in a list of html pages and iterate through them, extracting all words from the pre-processed html text.
    It will output a dictionary of words occuring the collection of pages.
    The dictionary keys are words that contain a list of occurrences and locations of where the terms are found in the documents.
    '''

    word_list = {}
    document_list = {}

    # Loop through each file in the zip container
    for name in list_of_pages:
        # Read the html file
        with open(name, 'r', encoding='utf-8', errors='ignore') as f:
            try:
                data = f.read()
            except:
                continue
        

        # Parse the data with BeautifulSoup
        soup = BeautifulSoup(data, 'html.parser')

        # Extract the text from the html file and generate a list of "words" separated by spaces
        page_text = soup.getText().split()

        if soup.title:
            doc_title = soup.find('title').getText()
        else:
            doc_title = name.split('/')[-1]

        # Add document to document_list
        document_list[name] = {
            'title': doc_title,
            'vector_length': 0,
            'max_freq': 0,
            'snippet': getSnippetfromHTML(data),
            }

        # Loop through words in extracted text and preprocess to exclude prohibited words
        doc_words = {}
        for id, word in enumerate(page_text):

            # Check if word contains only letters
            if word.isalpha() and word.lower() not in stop_words:
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
    
    return word_list, document_list




with open('rhf_links.json') as f:
    pages = json.load(f)

corpus, document_list = buildHashMap(pages)

print(f'# of documents: {len(document_list)}')
print(f'# of words: {len(corpus)}')

with open('rhf_corpus.json', 'w') as f:
    json.dump(corpus, f)

with open('rhf_documents.json', 'w') as f:
    json.dump(document_list, f)