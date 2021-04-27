def naive(text, pattern):
    m = len(pattern)
    n = len(text)
    res = []
    for s in range(n - m + 1):
        if text[s:s + m] == pattern:
            res.append(s)
    return res


if __name__ == '__main__':
    print(naive("hhhh", "hh"))
    print(naive("abababab", 'ab'))
