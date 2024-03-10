Basic use
*********

Import
======
First, you need import the package ``cra`` as follows::
	
	from metpy.units import units
	from cra.air_sounding import AirSounding
	from cra.variables import VariablesSet

Load file and define variables
==============================
The file must be formatted in a CSV-like format.

.. note::
	To open ftr and cor files please see :ref:`the last section<file handle>`.

.. note::
	``VariablesSet`` uses ``pandas.read_csv`` to open files.

You can load it with ``VariablesSet``::
	
	v_set = VariablesSet('my_file.csv', delimiter=';')

All keywords arguments will be given to ``pandas.read_csv`` so please refer to the pandas documentation if you have any problems opening a file.

Once the file is open, you can define the variables in it. Basically, you should define:

* the pressure

* the temperature

* the dew point (this can also be calculated from temperature and relative humidity)

* the east wind component

* the north wind component

To do this you need to use the predefined methods::

	v_set.add_press(('Press', units.hPa))  # Press is the name of the pressure in the file
	v_set.add_temp(('T_air', units.degC))  # T_air is the name of the temperature in the file
	v_set.add_windu(('WE', units('m/s'))
	v_set.add_windv(('WN', units('m/s'))

In this exemple, the file does not contain the dew point so we have to calculate it::
	
	v_set.compute_dewpoint(('T_air', units.degC), ('RelU', units.percent))

Here ``'RelU'`` is the name of the relative humidity in the file.

Plots data
==========
Once all the variables are defined, we can create a new instance of ``AirSounding``::

	air_souding = AirSounding(v_set)

and plot the upper air sounding on a Skew-T diagram::

	air_sounding.show()

You can also try to find some layers into the upper air sounding::

	air_sounding.auto_layers(nb_layers=15, show=True)

.. _file handle:

Handle ftr and cor files
========================
This package also provide a module to simply handle ftr and core files. You can import it as follows::

	from cra.files import open_ftr, open_cor

You just need to give to the opening function the name of the file and the keywords argument to be given to pandas.read_csv::

	v_set = open_ftr('myfile.ftr', delimiter='\t')

