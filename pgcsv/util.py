from normality import normalize as text_normalize
from unicodedata import normalize as unicode_normalize


def normalize_column(name):
    name = name.replace('_', ' ')
    name = text_normalize(name)
    name = name.replace(' ', '_')
    name = unicode_normalize('NFKC', name)
    # column names can be 63 *bytes* max in postgresql
    while len(name.encode('utf-8')) >= 64:
        name = name[:len(name) - 1]
    return name
