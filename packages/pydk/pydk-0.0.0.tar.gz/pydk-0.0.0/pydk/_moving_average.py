
import numpy as np

def _moving_average(X, window_size):
    
    """
    Calculate the moving average over a given window of an array. 
    
    Parameters:
    -----------
    X
        1-D array of values.
    
    window_size
        Number of items over which values should be smoothed. 
    
    
    Returns:
    --------
    Array of a moving average of array values using the given window.
    """
    
    window = np.ones(int(window_size))/float(window_size)
    
    return np.convolve(X, window, 'same')