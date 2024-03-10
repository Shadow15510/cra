'''
This module provide a class to manipulate variables with dimensions.

Classes
-------
.. autoclass:: LockedWarning
.. autoclass:: VariablesSet
'''
from warnings import warn
import numpy as np
import pandas as pd
import metpy.calc as mpcalc


class LockedWarning(Warning):
    '''Warns the user that he's trying to modify a locked VariablesSet instance.'''


class VariablesSet:
    '''
    This class provides a standard format for passing variables to an AirSounding instance. It also
    allows data to be split between ascending and descending profiles.

    Attributes
    ----------
    data : pd.DataFrame, private
        The DataFrame that contains all the data from the upper air sounding.
    variables : dict, private
        Identified variables in ``data``. You can only identify the variables required by
        AirSounding, in particular :

        * the pressure;

        * the temperature;

        * the dewpoint;

        * the easterly wind;

        * the northerly wind.

    locked : bool, private
        ``False`` if the instance can still be edited.

    Methods
    -------
    .. automethod:: __init__
    .. automethod:: add_press
    .. automethod:: add_temp
    .. automethod:: add_dewpoint
    .. automethod:: add_windu
    .. automethod:: add_windv
    .. automethod:: compute_dewpoint
    .. automethod:: apply_threshold
    '''
    def __init__(self, filename: str, **kwargs):
        '''Constructor method'''
        self.__data = pd.read_csv(filename, **kwargs)
        self.__data.dropna(inplace=True)
        self.__variables = {}
        self.__locked = False

    def __getitem__(self, varname: str):
        '''
        Returns the called variable
        
        Parameters
        ----------
        varname: str
            The name of the requested variable.
        '''
        return self.__variables[varname]

    def add_press(self, vardata: tuple):
        '''
        Adds pressure to ``variables``.

        Parameters
        ----------
        vardata : tuple
            This tuple must contains:

            * the name of the pressure in ``data``;

            * the unit of the pressure in ``data`` (cf. ``metpy.units``).

        Warns
        -----
        LockedWarning
            This warning should appear if you try to add a pressure when the VariablesSet is locked.
        '''
        if not self.__locked:
            self.__variables['press'] = self.__data[vardata[0]].values * vardata[1]
        else:
            warn(
                    'this instance of VariableSet is locked, you cannot add a new variable to it',
                    LockedWarning
                )

    def add_temp(self, vardata: tuple):
        '''
        Adds temperature to ``variables``.

        Parameters
        ----------
        vardata : tuple
            This tuple must contains:

            * the name of the temperature in ``data``;

            * the unit of the temperature in ``data`` (cf. ``metpy.units``).

        Warns
        -----
        LockedWarning
            This warning should appear if you try to add a temperature when the VariablesSet is
            locked.
        '''
        if not self.__locked:
            self.__variables['temp'] = self.__data[vardata[0]].values * vardata[1]
        else:
            warn(
                    'this instance of VariableSet is locked, you cannot add a new variable to it',
                    LockedWarning
                )

    def add_dewpoint(self, vardata: tuple):
        '''
        Adds dewpoint to ``variables``.

        Parameters
        ----------
        vardata : tuple
            This tuple must contains:

            * the name of the dewpoint in ``data``;

            * the unit of the dewpoint in ``data`` (cf. ``metpy.units``).

        Warns
        -----
        LockedWarning
            This warning should appear if you try to add a dewpoint when the VariablesSet is locked.
        '''
        if not self.__locked:
            self.__variables['dewpoint'] = self.__data[vardata[0]].values * vardata[1]
        else:
            warn(
                    'this instance of VariableSet is locked, you cannot add a new variable to it',
                    LockedWarning
                )

    def add_windu(self, vardata: tuple):
        '''
        Adds east wind component to ``variables``.

        Parameters
        ----------
        vardata : tuple
            This tuple must contains:

            * the name of the east wind component in ``data``;

            * the unit of the east wind component in ``data`` (cf. ``metpy.units``).

        Warns
        -----
        LockedWarning
            This warning should appear if you try to add an east component of the wind when the
            VariablesSet is locked.
        '''
        if not self.__locked:
            self.__variables['wind_u'] = self.__data[vardata[0]].values * vardata[1]
        else:
            warn(
                    'this instance of VariableSet is locked, you cannot add a new variable to it',
                    LockedWarning
                )

    def add_windv(self, vardata: tuple):
        '''
        Adds north wind component to ``variables``.

        Parameters
        ----------
        vardata : tuple
            This tuple must contains:

            * the name of the north wind component in ``data``;

            * the unit of the north wind component in ``data`` (cf. ``metpy.units``).

        Warns
        -----
        LockedWarning
            This warning should appear if you try to add a north component of the wind when the
            VariablesSet is locked.
        '''
        if not self.__locked:
            self.__variables['wind_v'] = self.__data[vardata[0]].values * vardata[1]
        else:
            warn(
                    'this instance of VariableSet is locked, you cannot add a new variable to it',
                    LockedWarning
                )

    def compute_dewpoint(self, temperature: tuple, relative_humitidy: tuple):
        '''
        Computes the dewpoint from the air temperature and the relative humidity.

        Parameters
        ----------
        temperature : tuple
            This tuple must contains:

                * the name of the temperature in ``data``;

                * the unit of the temperature in ``data`` (cf. ``metpy.units``).

        relative_humidity : tuple
            This tuple must contains:

                * the name of the relative humidity in ``data``;

                * the unit of the relative humidity in ``data`` (cf. ``metpy.units``).

        Warns
        -----
        LockedWarning
            This warning should appear if you try to compute the dewpoint when the
            VariablesSet is locked.
        '''
        if 'dewpoint' in self.__variables:
            raise KeyError('there\'s already an entry for the dewpoint')

        if not self.__locked:
            self.__variables['dewpoint'] = mpcalc.dewpoint_from_relative_humidity(
                    self.__data[temperature[0]].values * temperature[1],
                    self.__data[relative_humitidy[0]].values * relative_humitidy[1]
                ).to('degC')
        else:
            warn(
                    'this instance of VariableSet is locked, you cannot add a new variable to it',
                    LockedWarning
                )

    def apply_threshold(self, threshold: float, ascending: bool=True):
        '''
        This function cuts data by applying a threshold to the pressure. It will retain all data
        above this threshold. You can also request an ascending or descending profile for altitude
        sounding.

        .. warning::
            Applying a threshold will lock the ``VariablesSet`` instance.

        Parameters
        ----------
        threshold : float
            The threshold to apply on pressure, all pressure above this value will be retain.
        ascending : bool, optionnal (``True`` by default)
            Indicates which profile you want to keep. If ``ascending`` is set on ``True`` it will
            keep the ascending profile, otherwise the descending profile.

        Warns
        -----
        LockedWarning
            This warning should appear if you try to apply a threshold when the
            VariablesSet is locked.
        '''
        if not self.__locked:
            threshold = np.where(
                    np.isclose(self.__variables['press'].magnitude, threshold)
                )[0]

            if ascending:
                threshold = threshold[0]
                for var in self.__variables:
                    self.__variables[var] = self.__variables[var][: threshold]
            else:
                threshold = threshold[1]
                for var in self.__variables:
                    self.__variables[var] = np.flip(self.__variables[var][threshold: ])

        else:
            warn(
                    'this instance of VariableSet is locked, you cannot add a new variable to it',
                    LockedWarning
                )
