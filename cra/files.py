'''
This little module gives some functions to handle common file formats.

Functions
---------
.. autofunction:: open_ftr
.. autofunction:: open_cor
'''
from metpy.units import units
from cra.variables import VariablesSet


def open_ftr(filename: str, **kwargs):
    '''
    Opens and creates a ``VariablesSet`` instance from a ftr file.

    Parameters
    ----------
    filename : str
        The name of the ftr file to be read.
    kwargs:
        The keywords argument to be given to ``pandas.read_csv``.

    Returns
    -------
    v_set : VariablesSet
        The ``VariablesSet`` instance, ready to be given to ``AirSounding``.
    '''
    v_set = VariablesSet(filename, **kwargs)
    v_set.add_press(('ftr_pres', units.hPa))
    v_set.add_temp(('ftr_temp', units.degC))
    v_set.add_dewpoint(('ftr_DP', units.degC))
    v_set.add_windu(('ftr_VEF', units('m/s')))
    v_set.add_windv(('ftr_VNF', units('m/s')))
    return v_set


def open_cor(filename: str, **kwargs):
    '''
    Opens and creates a ``VariablesSet`` instance from a cor file.

    Parameters
    ----------
    filename : str
        The name of the cor file to be read.
    kwargs:
        The keywords argument to be given to ``pandas.read_csv``.

    Returns
    -------
    v_set : VariablesSet
        The ``VariablesSet`` instance, ready to be given to ``AirSounding``.
    '''
    v_set = VariablesSet(filename, **kwargs)
    v_set.add_press(('Press', units.hPa))
    v_set.add_temp(('TaCal', units.degC))
    v_set.compute_dewpoint(('TaCal', units.degC), ('UCal', units.percent))
    v_set.add_windu(('VE', units('m/s')))
    v_set.add_windv(('VN', units('m/s')))
    return v_set
