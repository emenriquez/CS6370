from bs4 import BeautifulSoup
from os import path
import json

def recursiveSpider(index='rhf/index.html'):
    '''
    This function takes an index and performs (hopefully) a depth-first search throughout all available links in anchor tags.
    The search starts at the html page passed in through "index" in the directory that you want to search.
    The function references and writes to global variables. I added this since it is recursive so each branch works with the most updated information
    '''
    global count, link_set
    
    link_set.update([index])

    with open(index, 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')

        for child in soup('a'):
            next_link = child.get("href")

            # domain needs to be added to address since links are relative to current page
            domain = '/'.join(index.split('/')[:-1]) + '/'
            next_link = domain + next_link

            # check if the link in is the folder, also I think '..' links are breadcrumbs, this was needed to prevent the links from looping on themselves forever
            if next_link not in link_set and path.exists(next_link) and '..' not in next_link:
                try:
                    count += 1
                    print(f"# of links found: {count}\r", end="")
                    link_set.update(recursiveSpider(next_link))
                except:
                    pass
                    
    
    return [link_set]

    
count=0
link_set = set()

all_links = recursiveSpider('rhf/index.html')

# Since the last item returned is also a list with a set inside, grab the first item of the list
with open('rhf_links.json', 'w') as f:
    json.dump(sorted(all_links[0]), f)
