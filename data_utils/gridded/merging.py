"""
Contains methods for merging gridded data.
"""

import numpy


def stack_datasets(bottom, top, mask=None):
    """
    Stacks one dataset on top of another.

    If a mask argument is provided, then the final dataset will be equal to the
    top dataset wherever mask=1, and the bottom dataset everywhere else.

    If a mask argument is not provided, then the final dataset will be equal
    to the top dataset wherever the top dataset is not missing, and the
    bottom dataset everywhere else.

    Parameters
    ----------

    - bottom (2-d array)
        - 2-dimensional (lat x lon) Numpy array of data to serve as the bottom
          dataset
    - top (2-d array)
        - 2-dimensional (lat x lon) Numpy array of data to serve as the top
          dataset
    - mask (2-day array, optional)
        - 2-dimensional (lat x lon) Numpy array, set to 1 wherever you would
          like the top dataset to be selected

    Examples
    --------


    """
    if mask:
        # Wherever the mask is 1, set final_grid to the top dataset, bottom
        # elsewhere
        final_grid = numpy.where(mask == 1, top, bottom)
    else:
        # Wherever the top dataset is not NAN, set final_grid to the top
        # dataset, bottom elsewhere
        final_grid = numpy.where(~numpy.isnan(top), top, bottom)

    return final_grid
