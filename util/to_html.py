from dominate import tags

def link_to_html(value):
    if not isinstance(value, str):
        raise Exception("Passed non string as link")
    return str(tags.a(value, href=value, target="_blank"))

def list_to_html(value):
    if not isinstance(value, list):
        raise Exception("Passed non-list as a list")
    l = tags.ul()
    for el in value:
        l += tags.li(el)
    return str(l)

def dict_to_html(value):
    if not isinstance(value, dict):
        raise Exception("Passed non-dict as a dict")

    with tags.table() as table:
        with tags.tbody() as tbody:
            for k, v in value.items():
                with tags.tr() as row:
                    tags.td(k)
                    tags.td(v)
    return str(table)


def table_to_html(value):
    if not isinstance(value, dict):
        raise Exception("Passed non-dict as a table")
    if not all(len(listA) == len(listB)
        for listA in value.values() for listB in value.values()):
        raise Exception("Provided lists do not have the same length")

    columns = value.keys()
    with tags.table() as table:
        with tags.thead() as head:
            for col in columns:
                tags.th(col)
        with tags.tbody() as body:
            tuples = zip(*value.values())
            for row in tuples:
                with tags.tr() as html_row:
                    for val in row:
                        if val is None:
                            val = "None"
                        tags.td(val)
    return str(table)
