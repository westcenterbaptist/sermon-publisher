def end_with_slash(path):
    if not path.endswith('/'):
        path += '/'
    return path