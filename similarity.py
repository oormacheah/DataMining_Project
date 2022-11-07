'''
Similarity measures for stack traces
'''

def jaccard(a, b):
    set_a = set(a)
    set_b = set(b)

    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))

    return intersection / union

def jaccard_df(s, s_copy, index, distinct=True):
    if distinct:
        return s_copy.apply(lambda x: jaccard(x, s)).tolist()[index + 1:]
    else:
        return s_copy.apply(lambda x: jaccard(x, s)).tolist()

