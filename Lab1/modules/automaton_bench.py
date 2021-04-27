from time import time


def automaton(text, pattern):

    def generate_delta_function():

        def sigma_function(P):
            k = len(P)
            for i in range(k):
                if P[i:] == pattern[:k - i]:
                    return k - i
            return 0

        alphabet_dict = {}
        for c in pattern:
            alphabet_dict[c] = 0

        delta_f = [alphabet_dict.copy() for i in range(m + 1)]
        for i in range(m + 1):
            for c in alphabet_dict.keys():
                delta_f[i][c] = sigma_function(pattern[:i] + c)

        return delta_f

    ti1 = time()
    m = len(pattern)
    delta_f = generate_delta_function()
    ti2 = time()
    tm1 = time()
    q = 0   # current state
    res = []
    for i, c in enumerate(text):
        q = delta_f[q].get(c, 0)
        if q == m:
            res.append(i - m + 1)
    tm2 = time()
    return {'matches': res, 'times': {'init_time': ti2 - ti1, 'matching_time': tm2 - tm1}}


if __name__ == '__main__':
    print(automaton("hhhh", "hh"))
    print(automaton("abababab", 'ab'))
