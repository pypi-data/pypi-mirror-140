"""Provide a string as an input to the stringmix() function."""

def stringmix(string):
    """Provide a string, and receive a shuffled version of that string."""
    import random
    list_string = list(string)
    random.shuffle(list_string)
    return ''.join(list_string)
