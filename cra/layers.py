'''
This module provides functions for dividing a signal into layers by analyzing the strongest
gradients into the input signal.

Functions
---------
.. autofunction:: chech_indices_spacing
.. autofunction:: get_layers
'''
import numpy as np

def check_indices_spacing(indices: list, index_to_check: int, min_dist: int):
    '''
    Checks that the index to be checked is far enough away from all the others.

    Parameters
    ----------
    indices : list
        All the indices, they're considered as a reference.
    index_to_check : int
        The index to be checked.
    min_dist : int
        The minimum distance beetween two indices.

    Returns
    -------
    out : bool
        It equals ``True`` if ``index_to_check`` is far enough away from all the others, and
        ``False`` in the other case.
    '''
    for i in indices:
        if abs(index_to_check - i) <= min_dist:
            return False
    return True


def get_layers(layer_size: int, nb_layers: int, *datas):
    '''
    Extracts strongest gradients from input data. If you give several input datas, the result will
    be the concatenation of all the gradients found.

    Parameters
    ----------
    layer_size : int
        The minimum size of each layer (in terms of index). The input datas will be divided into
        small layers of this size, and the sliding gradients will be computed on these layers.
    nb_layers : int
        The numbers of layers you want.
    *datas
        All the data on which you you wish to obtain the strongest gradients.

    Returns
    -------
    out : list
        The sorted list of the indices of all the strongest gradients.

    Exemple
    -------
    If you're searching for small phenomena into an upper air sounding, you should pass a small
    ``layer_size``. You also have two variables from the sounding (e.g. temperature and humidty)
    and you want 10 layers::

        layers_indices = get_layers(10, 10, data_temp, data_relative_hum)
    '''
    final_indices = set()
    nb_layers //= len(datas)

    for data in datas:
        nb_data = len(data)
        gradients = []
        for i in range(nb_data - layer_size):
            grads = np.abs(np.gradient(data[i: i + layer_size]))
            gradients.append((
                    i,
                    sum(grads) / layer_size
                ))

        indices = [0]
        while len(indices) < nb_layers and gradients:
            grad_max = max(gradients, key=lambda x: x[1])
            gradients.remove(grad_max)
            if check_indices_spacing(indices, grad_max[0], layer_size):
                indices.append(grad_max[0])
                indices.append(grad_max[0] + layer_size)
        indices.append(nb_data - 1)

        final_indices = {*final_indices, *indices}

    return sorted(list(final_indices))
