

def person_sort_name(name, first_delimiter=' '):
    n = name.split()
    n.insert(0, n.pop())
    if len(n) == 1:
        return n[0]
    elif len(n) > 1:
        return n[0] + first_delimiter + ' '.join(n[1:])
    return ''
