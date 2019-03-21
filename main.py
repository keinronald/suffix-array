"""
SUFFIX-ARRAY-SUCHE
Die Suche is case-sensitiv
Ronald Keinberger
"""

import timeit

results = []
txt = open('data/text.txt')
fulltext = txt.read()
fulltext += "$"
search_patterns = ["Sherlock", "hound", "Watson"]


"""
Task 2 - 0
- construct s12
- sort s12 suffixes
- sort s0 suffix
"""


def create_sa(text):
    """ Task 2 - 0 """
    # construct s12
    s12_unsorted = create_s12(text)

    # sort s12 suffixes
    s12_with_ranks = bucketsort(text, s12_unsorted)
    s12_ranks = [value[0] for value in s12_with_ranks]

    if len(set(s12_ranks)) == len(s12_ranks):
        s12 = [value[1] for value in sorted(s12_with_ranks, key=lambda x: x[0])]
    else:
        sa_s12 = create_sa(s12_ranks)
        s12 = [s12_with_ranks[idx][1] for idx in sa_s12]

    # sort s0 suffix
    s0 = create_s0(text, s12)

    """ Task 2 - 1"""
    # create inverse sa
    inverse_sa = create_inverse_sa(len(text), s12)
    merged_sa = merge_sa(text, s0, s12, inverse_sa)

    return merged_sa


# construct s12
def create_s12(text):
    # creating the array
    s1 = []
    s2 = []

    # filling the triplet arrays
    for idx in range(len(text)):
        if (idx % 3) == 1:
            s1.append(idx)
        elif (idx % 3) == 2:
            s2.append(idx)
    return s1 + s2


# sort s12 suffixes
def bucketsort(text, sa, s0=False):
    triplet_idx = 2
    if s0:
        triplet_idx = 0
    sorted_sa = sa

    # sort the sa
    for i in range(triplet_idx, -1, -1):
        buckets = dict()

        for text_idx in sorted_sa:
            triplet = get_triplet(text, text_idx)

            checked_i = i if i < len(triplet) else len(triplet) - 1

            if triplet[checked_i] not in buckets:
                buckets[triplet[checked_i]] = []

            buckets[triplet[checked_i]].append(text_idx)

        sorted_sa = []

        for key in sorted(buckets.keys()):
            sorted_sa += buckets[key]

    # get the ranks
    ranks = dict()
    rank = 1

    for text_idx in sorted_sa:
        triplet = ''.join([str(x) for x in get_triplet(text, text_idx)])
        if triplet not in ranks:
            ranks[triplet] = rank
            rank += 1

    # combine s12 and ranks
    s12_with_ranks = [(ranks.get(''.join([str(x) for x in get_triplet(text, idx_original)])), idx_original) for idx_original in sa]

    return s12_with_ranks


def get_triplet(text, idx):
    triplet = []
    for text_idx in range(idx, min(idx+3, len(text))):
        triplet.append(text[text_idx])

    while len(triplet) < 3 and isinstance(triplet, str):
        triplet.append("$")

    return triplet


# sort s0 suffix
def create_s0(text, s12):
    s0_unsorted = []

    # create the s0 sorted by the second letter
    for idx_text in s12:
        if ((idx_text - 1) % 3) == 0:
            s0_unsorted.append(idx_text - 1)

    if len(text) % 3 == 1:
        s0_unsorted.insert(0, len(text) - 1)

    # sort the s0 - but only the by the first letter
    s0_with_ranks = bucketsort(text, s0_unsorted, s0=True)

    # extract the values for s0
    s0 = [x[1] for x in sorted(s0_with_ranks, key=lambda x: x[0])]
    return s0


"""
Task 2 - 1
- merge s0 and s12
- for this you need to create the inverse_sa
"""


# create the inverse sa for the merge
def create_inverse_sa(len_text, sa):
    inverse_sa = [-1] * len_text

    for sa_idx in range(len(sa)):
        inverse_sa[sa[sa_idx]] = sa_idx

    return inverse_sa


def merge_sa(text, s0, s12, inverse_sa):
    sa = []
    idx_s0 = 0
    idx_s12 = 0

    while (idx_s0 + idx_s12) < (len(s0) + len(s12)):
        # wenn von einem keine eintraege mehr uebrig sind
        if idx_s0 >= len(s0):
            sa.append(s12[idx_s12])
            idx_s12 += 1
            continue

        if idx_s12 >= len(s12):
            sa.append(s0[idx_s0])
            idx_s0 += 1
            continue

        current_s0 = s0[idx_s0]
        current_s12 = s12[idx_s12]

        # check for first char
        if text[current_s0] > text[current_s12]:
            sa.append(current_s12)
            idx_s12 += 1
            continue

        if text[current_s0] < text[current_s12]:
            sa.append(current_s0)
            idx_s0 += 1
            continue

        if text[current_s0] == text[current_s12]:

            i = 1
            while True:
                # check with inverse_sa
                if (current_s0 + i) % 3 == 0 or (current_s12 + i) % 3 == 0:
                    # check for second char
                    if text[current_s0 + i] > text[current_s12 + i]:
                        sa.append(current_s12)
                        idx_s12 += i
                        break

                    if text[current_s0 + i] < text[current_s12 + i]:
                        sa.append(current_s0)
                        idx_s0 += i
                        break

                    if text[current_s0 + i] == text[current_s12 + i]:
                        i += 1
                        continue
                    continue

                if inverse_sa[current_s0 + i] > inverse_sa[current_s12 + i]:
                    sa.append(current_s12)
                    idx_s12 += 1
                    break

                if inverse_sa[current_s0 + i] < inverse_sa[current_s12 + i]:
                    sa.append(current_s0)
                    idx_s0 += 1
                    break

    return sa


"""
Task 2 - 2
- repeat task 1
- create lcp
- create llcp & rlcp
- implement the search
- count the results
"""


# generate the llcp and the rlcp
def precompute_binary_lcps(lcp1):
    llcp = [None] * (len(lcp1))
    rlcp = [None] * (len(lcp1))

    def rekursive_binary_lcps(l, r):
        if l == r-1:
            return lcp1[l]
        m = (l + r) // 2
        llcp[m] = rekursive_binary_lcps(l, m)
        rlcp[m] = rekursive_binary_lcps(m, r)
        return min(llcp[m], rlcp[m])
    rekursive_binary_lcps(0, len(lcp1))
    return llcp, rlcp


# precompute the lcp
def create_lcp(t, sa, inverse_sa):
    l = 0
    lcp = [0] * len(t)
    for i in range(len(t)):
        k = inverse_sa[i]
        if k + 1 < len(t):
            j = sa[k + 1]
            while t[i + l] == t[j + l]:
                l += 1
            lcp[k] = l
            if l > 0:
                l = l - 1
        else:
            l = 0
            lcp[k] = l

    return lcp


# find one id in the suffix-array where the searchtext matches
def search_suffix_binary(t, sa, p, lcp_lr):
    lcp_l = lcp_lr[0]
    lcp_r = lcp_lr[1]

    l = 0
    r = len(sa)
    lcp_pl = 0
    lcp_pr = 0
    while True:
        c = (l + r) // 2
        left_part = True
        compare = False
        i = min(lcp_pl, lcp_pr)

        if lcp_pl > lcp_pr:
            if lcp_l[c] > lcp_pl:
                left_part = False
            elif lcp_l[c] < lcp_pl:
                left_part = True
            elif lcp_l[c] == lcp_pl:
                compare = True

        else:
            if lcp_r[c] > lcp_pr:
                left_part = True
            elif lcp_r[c] < lcp_pr:
                left_part = False
            elif lcp_r[c] == lcp_pr:
                compare = True

        if compare:
            while (i < len(p)) and (sa[c] + i < len(t)):
                if p[i] < t[sa[c] + i]:
                    break

                elif p[i] > t[sa[c] + i] or len(p) <= i:
                    left_part = False
                    break

                elif len(p) > len(t[sa[c]:]):
                    left_part = False
                    break

                i += 1

            if len(p) <= i:
                return c

        if left_part:
            if c == l + 1:
                if i < len(p):
                    return False
                return c

            r = c
            lcp_pr = i

        else:
            if c == r - 1:
                if i < len(p):
                    return False
                return r

            l = c
            lcp_pl = i


# count how often the pattern is in the text
def count_results(sa_id, pattern_length, lcp):
    if not sa_id:
        return 0
    i = sa_id
    count = 1
    while pattern_length <= lcp[i]:
        count += 1
        i += 1

    i = sa_id - 1
    while pattern_length <= lcp[i]:
        i -= 1
        count += 1

    return count

if __name__ == "__main__":
    # preprocess
    sa = create_sa(fulltext)
    inverse_sa = create_inverse_sa(len(fulltext), sa)
    lcp = create_lcp(fulltext, sa, inverse_sa)
    lcp_lr = precompute_binary_lcps(lcp)

    # search
    for search_pattern in search_patterns:
        print("##### searched for", search_pattern, "#####")

        # start the timer
        start = timeit.default_timer()

        # search the phrase
        sa_id = search_suffix_binary(fulltext, sa, search_pattern, lcp_lr)
        amount = count_results(sa_id, len(search_pattern), lcp)

        # stop the timer
        stop = timeit.default_timer()

        print("Suchbegriff:", search_pattern)
        print('Anzahl des Suchbegriffs: ', amount)
        print('Time: ', round((stop - start) * 1000, 3), 'ms')
        print()
