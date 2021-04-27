from time import time


def kmp(text, pattern):

    def generate_prefix_function():
        prefix_function = [0] * m
        k = 0
        for q in range(1, m):
            while k > 0 and pattern[k] != pattern[q]:
                k = prefix_function[k - 1]
            if pattern[k] == pattern[q]:
                k += 1
            prefix_function[q] = k
        return prefix_function

    ti1 = time()
    m = len(pattern)
    prefix_function = generate_prefix_function()
    ti2 = time()
    tm1 = time()
    res = []
    q = 0
    for i, c in enumerate(text):
        while q > 0 and pattern[q] != c:
            q = prefix_function[q - 1]
        if pattern[q] == c:
            q += 1
        if q == m:
            res.append(i - m + 1)
            q = prefix_function[q - 1]
    tm2 = time()
    return {'matches': res, 'times': {'init_time': ti2 - ti1, 'matching_time': tm2 - tm1}}


if __name__ == '__main__':
    print(kmp("hhhh", "hh"))
    print(kmp("abababab", 'ab'))
