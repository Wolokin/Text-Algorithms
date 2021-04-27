from time import time


def naive(text, pattern):
    t1 = time()
    m = len(pattern)
    n = len(text)
    res = []
    for s in range(n - m + 1):
        if text[s:s + m] == pattern:
            res.append(s)
        # # Alternative string comparison without using Python optimizations
        # for i in range(m):
        #     if text[s + i] != pattern[i]:
        #         break
        # else:
        #     res.append(s)
    t2 = time()
    return {'matches': res, 'times': {'init_time': 0.0, 'matching_time': t2 - t1}}


if __name__ == '__main__':
    print(naive("hhhh", "hh"))
    print(naive("abababab", 'ab'))
