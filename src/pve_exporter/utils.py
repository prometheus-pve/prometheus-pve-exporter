def get_key_tuple(key: str, tuple: tuple) -> str:
    """Get the value of a key in a tuple of tuples."""
    for item in tuple:
        if item[0] == key:
            return item[1]
    return ''