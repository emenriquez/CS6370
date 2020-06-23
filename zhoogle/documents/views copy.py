from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.generic.base import TemplateView
from django.db.models import Sum, Q

from .models import Document, Word, Occurrence
import string
import math
from .forms import SearchForm

def NewSearch(input):
    results = set()
    not_results = set()
    # Preprocessing of query
    exclude = set(string.punctuation)
    no_punctuation = ''.join(char for char in input if char not in exclude)

    # Add OR terms
    or_query = no_punctuation.split(' or ')
    if len(or_query) > 1:
        for subquery in or_query:
            results.update(NewSearch(subquery))
    
    # test for AND terms
    and_query = no_punctuation.split(' and ')
    if len(and_query) > 1:
        for i, subquery in enumerate(and_query):
            if i == 0:
                results.update(NewSearch(subquery))
            else:
                results.intersection_update(NewSearch(subquery))

    # Remove NOT terms
    not_query = no_punctuation.split(' not ')
    if len(not_query) > 1:
        for i, subquery in enumerate(not_query):
            if i == 0:
                results.update(NewSearch(subquery))
            else:
                not_results.update(NewSearch(subquery))

    # Vector space model
    if len(not_query) == 1 and len(and_query) == 1 and len(or_query) == 1:
        for word in no_punctuation.split():
            docs = Occurrence.objects.filter(word=word).values_list('doc_id', flat=True)
            results.update(docs)
    results.difference_update(not_results)

    return results

def RankResults(query, results):

    # convert set to Queryset
    primary_keys = [result for result in results]
    results = Occurrence.objects.filter(doc_id__in=primary_keys)

    # Preprocessing of query
    exclude = set(string.punctuation)
    no_punctuation = ''.join(char for char in query if char not in exclude)
    operators = ['and', 'or', 'not']
    query = [word.lower() for word in no_punctuation.split() if word not in operators]

    results = results.filter(word__in=query)
    ordered_results = results.values_list('doc_id').annotate(Sum('tf_idf')).order_by('-tf_idf__sum')
    rankings = [Document.objects.get(id=result[0]) for result in ordered_results[:100]]

    return rankings

def PhrasalSearch(query):
    exclude = set(string.punctuation)
    stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
    no_punctuation = ''.join(char for char in query if char not in exclude)
    phrase = [word.lower() for word in no_punctuation.split() if word not in stop_words]

    # Find documents that have all words
    documents = []
    final_documents = set()
    for word in phrase:
        temp_docs = set(Occurrence.objects.filter(word=word).values_list('doc_id', flat=True))
        documents.append(temp_docs)
    
    if len(documents) == 0:
        return []

    document_set = set.intersection(*documents)
    hits = Occurrence.objects.filter(doc_id__in=document_set).filter(word__in=phrase)

    final_document_results = []
    for doc in document_set:
        docscore = 0
        temp_results = hits.filter(doc_id=doc)
        for id, word in enumerate(phrase):
            if id == 0:
                hit = temp_results.filter(word=word).values_list('locations', flat=True)[0]
                locations = [int(location) for location in hit.strip('][').split(', ')]
                next_locations = [location + 1 for location in locations] + [location + 2 for location in locations]
                prev_locations = [location - 1 for location in locations] + [location - 2 for location in locations]
                location_range = sorted(locations + next_locations + prev_locations)
                docscore = 1
            else:
                hit = temp_results.filter(word=word).values_list('locations', flat=True)[0]
                new_locations = [int(location) for location in hit.strip('][').split(', ')]
                for location in new_locations:
                    if location in location_range:
                        location_range.append(location+1)
                        docscore += 1
                    else:
                        continue

        if docscore >= len(phrase):
            final_document_results.append(doc)

    scores = "I'm pretty sure this is what you're looking for"

    final_result = [(Document.objects.get(id=doc), scores) for doc in final_document_results]

    return final_result

# Old search
def BooleanSearch(input):
    results = set()
    # Preprocessing of query
    exclude = set(string.punctuation)
    no_punctuation = ''.join(char for char in input if char not in exclude or char =='-')
    query = no_punctuation.split()

    # Union any other terms
    for id, word in enumerate(query):
        if id == 0:
            docs = Occurrence.objects.filter(word=word.lower())
            results.update(docs)
        else:
            if query[id - 1] == 'and':
                continue
            if query[id - 1] == 'or':
                docs = Occurrence.objects.filter(word=word.lower())
                results.update(docs)
    
    # Intersect set for any AND terms
    for id, word in enumerate(query):
        if word == 'and':
            docs = Occurrence.objects.filter(word=query[id + 1])
            results.intersection_update(docs)

    # Exclude any NOT terms
    for id, word in enumerate(query):
        if word == 'not':
            docs = Occurrence.objects.get(word=query[id + 1])
            results.difference_update(exclusion_set)

    # Check database for query words
    query_string = f"Your Search: {' '.join(query)}"


    return query_string, results

def Homepage(request, *args, **kwargs):
    search = SearchForm(request.POST or None)
    query = request.GET.get('q', '')
    query_string, results = BooleanSearch(query)
    return render(request, "home.html", {'documents': results, 'search': search, 'query_string': query_string})

def Result(request, *args, **kwargs):
    query = request.GET.get('doc', '')
    testing = loader.render_to_string(query)
    return render(request, 'test.html', {'doc': testing})

def NewView(request, *args, **kwargs):
    search = SearchForm(request.POST or None)
    query = request.GET.get('q', '')
    if '"' in query:
        scores = PhrasalSearch(query)
    else:
        results = NewSearch(query)
        scores = RankResults(query, results)
    return render(request, "NewHome.html", {'documents': scores, 'search': search, 'query_string': query})
