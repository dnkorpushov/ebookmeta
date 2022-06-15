import os 
import re
import pathlib

def xstr(string):
    if string is None:
        return ''
    else:
        return str(string)


def str_to_list(s):
    return [x.strip() for x in s.split(',')]

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


def replace_keywords(s, m):

    def expand_keyword(s, key, val):
        if s.count(key) > 0:
            return s.replace(key, val), True if val else False
        return s, False

    def expand_all(s, m):

        expanded = False

        sorted_m = {}
        for k in sorted(m, key=len, reverse=True):
            sorted_m[k] = m[k]

        for key in sorted_m:
            s, ok = expand_keyword(s, key, sorted_m[key])
            expanded = expanded or ok
        
        if not expanded:
            return ''

        return s

    b_open = -1
    b_close = -1

    # Hack - I do not want to write real parser
    # s = s.replace(r'\{', chr(1)).replace(r'\}', chr(2))

    for i, sym in enumerate(s):
        if sym == '{':
            b_open = i
        elif sym == '}':
            b_close = i
            break
    if b_open >= 0 and b_close > 0 and b_open < b_close:
        s = replace_keywords(s[0:b_open] + expand_all(s[b_open + 1:b_close], m) + s[b_close + 1:], m)
    else:
        s = expand_all(s, m)

    return s


def split_ext(path):
    for ext in ['.fb2.zip']:
        if path.lower().endswith(ext):
            return ext
    return os.path.splitext(path)[1]

def replace_bad_symbols_(path):
    bad_symbols = '<>:"|*?'
    for s in bad_symbols:
        path = path.replace(s, '')
    return path

def normalize_path(path):
    def remove_illegal(s):
        illegal = '<>?:"*'
        for c in illegal:
            s = s.replace(c,'')
        return s

    def normalize_part(s: str) -> str:
        s = s.strip()
        if s.endswith('.'):
            s = s[0:-1]
    
        return remove_illegal(s)

    path = re.sub(r'\.+', '.', path)
    path = re.sub(r'\\+', r'\\', path)
    path = re.sub(r'\/+', '/', path)
    path = path.replace(r'\\', r'\\\\')

    p = pathlib.Path(path)
    clean_p = []

    if p.is_absolute():
        start = 1
        clean_p.append(p.anchor)
    else:
        start = 0
    for part in p.parts[start:]:
        clean_p.append(normalize_part(part))
    
    return str(pathlib.Path(*clean_p))