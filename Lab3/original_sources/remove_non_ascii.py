from unidecode import unidecode


def remove_non_ascii(text):
    return unidecode(text)


if __name__ == '__main__':
    filename = 'merged_linux_source'
    with open(filename + '.c', 'r') as f:
        text = f.read()
    text = remove_non_ascii(text)
    with open(filename + '_ascii.txt', 'w') as f:
        f.write(text)
