import numpy

def calculate_zncc(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Calculate ZNCC (Zero-mean Normalized Cross-Correlation) of 1D or 2D array.

    Parameters
    ----------
    a : np.ndarray
       1D or 2D array. Shape should be ('N', 'any1').
    b : np.ndarray
       1D or 2D array. Shape should be ('N', 'any2').

    Returns
    -------
    output : np.ndarray
      Scalar or 1D array or 2D array of ZNCC value. Shape is ('any1', 'any2').

    Examples
    --------
    Simple 1D array case
    >>> a = np.random.rand(10)
    >>> calculate_zncc(a, a) # same array
    1.0
    >>> calculate_zncc(a, -a) # invert array
    -1.0
    >>> calculate_zncc(a, 0.8*a+1.0) # change amplitude and offset
    1.0

    Simple image case
    >>> img = np.random.rand(256, 256, 3) 
    >>> calculate_zncc(img.flatten(), img.flatten())
    1.0

    2D array case
    >>> b = np.random.rand(10, 100)
    >>> c = np.random.rand(10, 200)
    >>> calculate_zncc(b, c).shape
    (100, 200)
    """
    # Check array shape
    N_a = a.shape[0]
    N_b = b.shape[0]
    assert N_a==N_b, f"Input array length must be same. {N_a}!={N_b}"

    # Subtract the average
    a = a - np.average(a, axis=0)
    b = b - np.average(b, axis=0)
    
    # Calculate the ZNCC
    aa_sum = np.expand_dims(np.sum(a*a, axis=0), -1)
    bb_sum = np.expand_dims(np.sum(b*b, axis=0), -1)
    output = ( a.T @ b ) / np.sqrt( aa_sum @ bb_sum.T )

    return output
