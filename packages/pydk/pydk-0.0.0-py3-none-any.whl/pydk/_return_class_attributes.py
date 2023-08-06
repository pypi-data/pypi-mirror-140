
def _return_class_attributes(obj, filter_startswith="__"):
    
    """
    Iterate over object attributes. Filter special sub-classes / methods (callables).
    
    
    obj
        python class object
    
    Notes:
    ------
    Source with other great examples / implementations:
    https://stackoverflow.com/questions/11637293/iterate-over-object-attributes-in-python
    """
    
    return [a for a in dir(obj) if not a.startswith(filter_startswith) and not callable(getattr(obj, a))]