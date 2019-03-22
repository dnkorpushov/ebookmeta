
def xstr(string):
    if string is None:
        return ''
    else:
        return str(string)


def person_sort_name(name, first_delimiter=' '):

    n = name.split()
    if len(n) > 0:
        n.insert(0, n.pop())
        if len(n) == 1:
            return n[0]
        elif len(n) > 1:
            return n[0] + first_delimiter + ' '.join(n[1:])
        return ''
    else:
        return ''
