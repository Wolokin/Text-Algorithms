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

    m = len(pattern)
    prefix_function = generate_prefix_function()
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
    return res


if __name__ == '__main__':
    print(kmp("hhhh", "hh"))
    print(kmp("abababab", 'ab'))
