import numpy as np

def Hits(page_list, num_iterations=5):
    '''
    This function is intended to produce rankings of pages according to the HITS algorithm.
    The input page_list: List of pages with the format (incoming_links, outgoing_links)
    After running the algorithm for the number of iterations, the function will return two lists:
        1. the "authority" scores of each page (based on inbound links)
        2. the "hub" scores of each input page (based on outbound links)
    '''
    a_score = [1]*len(page_list)
    h_score = [1]*len(page_list)

    for i in range(num_iterations):
        for id in range(len(page_list)):
            h_scores_sum = 0
            for page, (inbound, outbound) in enumerate(page_list):
                if id + 1 in outbound:
                    h_scores_sum += h_score[page]

            a_score[id] = h_scores_sum

        for id in range(len(page_list)):
            a_scores_sum = 0
            for page, (inbound, outbound) in enumerate(page_list):
                if id + 1 in inbound:
                    a_scores_sum += a_score[page]
                h_score[id] = a_scores_sum
        
        a_norm_factor = np.sqrt(sum([a*a for a in a_score]))
        h_norm_factor = np.sqrt(sum([h*h for h in h_score]))

        a_score = [a/a_norm_factor for a in a_score]
        h_score = [h/h_norm_factor for h in h_score]
        
    return a_score, h_score

def pageRank(page_list, alpha=0.15, num_iterations=5):
    '''
    This function is intended to produce rankings of pages according to the PageRank algorithm.
    The input page_list: List of pages with the format (incoming_links, outgoing_links)
    After running the algorithm for the number of iterations, the function will return a list of R scores
    '''
    num_pages = len(page_list)
    E = alpha/num_pages
    ranks = [1/num_pages]*num_pages
    new_ranks = [0]*num_pages

    for i in range(num_iterations):
        new_ranks = [0]*num_pages
        for p in range(num_pages):
            for q, (inbound, outbound) in enumerate(page_list):
                if p + 1 in outbound:
                    new_ranks[p] += ranks[q]/len(outbound)

            new_ranks[p] += E
        
        ranks = [rank/sum(new_ranks) for rank in new_ranks]
    
    return ranks
        




b = [([2], [3, 4]), ([4], [1, 3]), ([1, 2], [4]), ([1, 3], [2])]

for count in range(6):
    a_scores, h_scores = Hits(b, count)
    print(f'after iteration {count}:')
    for page in range(len(a_scores)):
        print(f' a{page+1} = {a_scores[page]:.3f}\t h{page+1} = {h_scores[page]:.3f}')


for count in range(6):
    ranks = pageRank(b, alpha=0.15, num_iterations=count)
    print(f'after iteration {count}:')
    for page in range(len(ranks)):
        print(f' R{page+1} = {ranks[page]:.3f}')
