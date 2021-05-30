from collections import defaultdict
from math import sqrt
from numba import njit
from Levenshtein import distance as levenshteinC
from pylcs import lcs2


@njit()
def lcs_metric(t1, t2):
    n = len(t1)
    m = len(t2)
    lcs = [[0 for i in range(m + 1)] for j in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if t1[i - 1] == t2[j - 1]:
                lcs[i][j] = lcs[i - 1][j - 1] + 1
    return 1 - (max([max(i) for i in lcs]) / max(n, m))


# Using a C library so the code will finish in a reasonable time
def lcs_metric2(t1, t2):
    return 1 - (lcs2(t1, t2) / max(len(t1), len(t2)))


#@njit()
def dice_metric(t1, t2, token_size=3):
    n = len(t1)
    m = len(t2)
    token_size = min([n, m, token_size])
    s1 = set([t1[i - token_size:i] for i in range(token_size, n + 1)])
    s2 = set([t2[i - token_size:i] for i in range(token_size, m + 1)])
    product = s1.intersection(s2)
    return 1 - (2 * len(product)) / (len(s1) + len(s2))


#@lru_cache(10000)
def ngram_stat(token, token_size):
    d = defaultdict(int)
    for i in range(token_size, len(token) + 1):
        d[token[i - token_size:i]] += 1
    return d


def scalar_on_dicts(d1, d2):
    res = 0
    for k, v in d1.items():
        res += v * d2[k]
    return res


#@njit()
def cosine_metric(t1, t2, token_size=3):
    if min(len(t1), len(t2)) < token_size:
        return 1
    d1 = ngram_stat(t1, token_size)
    d2 = ngram_stat(t2, token_size)
    return 1 - (scalar_on_dicts(d1, d2) /
                (sqrt(scalar_on_dicts(d1, d1)) * sqrt(scalar_on_dicts(d2, d2))))


@njit()
def levenshtein(s1, s2):
    n = len(s1)
    m = len(s2)
    distance = [[0 for i in range(m + 1)] for j in range(n + 1)]
    for i in range(n + 1):
        distance[i][0] = i
    for i in range(m + 1):
        distance[0][i] = i
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                distance[i][j] = distance[i - 1][j - 1]
            else:
                distance[i][j] = distance[i - 1][j]
                if distance[i][j] > distance[i][j - 1]:
                    distance[i][j] = distance[i][j - 1]
                if distance[i][j] > distance[i - 1][j - 1]:
                    distance[i][j] = distance[i - 1][j - 1]
                distance[i][j] += 1
    return distance[n][m] / max(n, m)


# Using a C library so the code will finish in a reasonable time
def levenshteinC_wrapper(s1, s2):
    return levenshteinC(s1, s2) / max(len(s1), len(s2))


if __name__ == '__main__':
    t1 = "abcdef"
    t2 = "bcdf"
    print(lcs_metric(t1, t2))
    print(dice_metric(t1, t2))
    print(cosine_metric(t1, t2))
