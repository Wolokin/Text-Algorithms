import random
from spacy.lang.pl import Polish
from lcs import lcs
from collections import defaultdict


def tokenize(text):
    nlp = Polish()
    return list(nlp.tokenizer(text))


def remove_random_elements_from_list(lis, p=0.03):
    to_remove = set(random.sample(lis, int(len(lis) * p)))
    return [x for x in lis if x not in to_remove]


def create_altered_file(origin_name, dest_name):
    with open(origin_name, "r") as f:
        text = f.read()
    with open(dest_name, "w") as f:
        tokens = remove_random_elements_from_list(tokenize(text))
        for token in tokens:
            f.write(token.text_with_ws)
    return tokens


def diff_files(filename1, filename2):
    with open(filename1, "r") as f:
        text1 = f.read()
    with open(filename2, "r") as f:
        text2 = f.read()
    tokens1 = [t.text_with_ws for t in tokenize(text1)]
    tokens2 = [t.text_with_ws for t in tokenize(text2)]
    diff(tokens1, tokens2)


def diff(tokens1, tokens2):

    def diff_from_common(tokens, common, rep):
        t, c = 0, 0
        line = 1
        diffs = defaultdict(list)
        while c < len(common):
            if tokens[t] != common[c]:
                diffs[line].append(tokens[t])
            else:
                c += 1
            line += tokens[t].count('\n')
            t += 1
        while t < len(tokens):
            diffs[line].append(tokens[t])
            line += tokens[t].count('\n')
            t += 1
        result = []
        for key, val in diffs.items():
            result.append((key, f"{rep} [{key}] " + repr(''.join(val))))
        return result

    common = lcs(tokens1, tokens2)[1]
    print(f"len1: {len(tokens1)}, len2: {len(tokens2)}, lcs: {len(common)}")
    diff1 = diff_from_common(tokens1, common, '<')
    diff2 = diff_from_common(tokens2, common, '>')
    difflist = sorted(diff1 + diff2)
    for line in difflist:
        print(line[1])


if __name__ == '__main__':
    origin_name = "../sources/romeo-i-julia-700.txt"
    f1 = "../sources/tokenized1.txt"
    f2 = "../sources/tokenized2.txt"
    tokens1 = create_altered_file(origin_name, f1)
    tokens2 = create_altered_file(origin_name, f2)
    print("===============Diff without retokenizing===============\n\n")
    diff([t.text_with_ws for t in tokens1], [t.text_with_ws for t in tokens2])
    print('\n\n===============Diff with retokenizing===============\n\n')
    diff_files(f1, f2)
