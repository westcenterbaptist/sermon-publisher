def end_with_slash(path):
    if not path.endswith('/'):
        path += '/'
    return path

def strip_break(string):
    return string.split('<br/>')