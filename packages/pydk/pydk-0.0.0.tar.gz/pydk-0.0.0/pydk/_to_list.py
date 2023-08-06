
def _to_list(arg):
    
    """
    Return a single item to a list or return the passed list.
    
    Parameters:
    -----------
    arg
        item to be turned into a list (or maintained as a list)
    
    Returns:
    --------
    list(arg) or arg
    
    Examples:
    ---------
    >>> from pyrequisites import to_list
    >>> to_list('something')
    ['something']
    
    >>> from pyrequisites import to_list
    >>> to_list(['something'])
    ['something']
    
    """
    
    if type(arg) == list:
        return arg
    else:
        return [arg]        