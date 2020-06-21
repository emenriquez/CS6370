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
