"""
This module allows to plot an upper air sounding on a Skew-T diagramm. It can also try to detect
interesting layers into the upper air sounding.

Classes
-------
.. autoclass:: AirSounding
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
from metpy.units import units
from metpy.plots import SkewT, Hodograph
from cra.layers import get_layers
from cra.variables import VariablesSet


# LaTeX-like font setup
matplotlib.rcParams["mathtext.fontset"] = "stix"
matplotlib.rcParams["font.family"] = "STIXGeneral"


class AirSounding:
    """
    Allows to plot and analyse an upper air sounding

    Attributes
    ----------
    nb_data : int
        The length of the given ``VariablesSet``.
    data : dict
        The variables contained into the given ``VariablesSet``.

    Methods
    -------
    .. automethod:: show
    .. automethod:: auto_layers
    """

    def __init__(self, variables: VariablesSet):
        """Constructor method."""
        self.nb_data = len(variables["press"])
        self.data = {
            "press": variables["press"].to("hPa"),
            "temp": variables["temp"].to("degC"),
            "p_temp": np.zeros(self.nb_data) * units.degC,
            "wbp_temp": np.zeros(self.nb_data) * units.degC,
            "wb_temp": np.zeros(self.nb_data) * units.degC,
            "dewpoint": variables["dewpoint"].to("degC"),
            "wind_u": variables["wind_u"].to("m/s"),
            "wind_v": variables["wind_v"].to("m/s"),
        }

        for index in range(self.nb_data):
            self.data["p_temp"][index] = mpcalc.potential_temperature(
                self.data["press"][index], self.data["temp"][index]
            ).to("degC")
            self.data["wbp_temp"][index] = mpcalc.wet_bulb_potential_temperature(
                self.data["press"][index],
                self.data["temp"][index],
                self.data["dewpoint"][index],
            ).to("degC")
            self.data["wb_temp"][index] = mpcalc.wet_bulb_temperature(
                self.data["press"][index],
                self.data["temp"][index],
                self.data["dewpoint"][index],
            ).to("degC")

    def __layers_analysis(self, layers: list):
        """
        Analyses the found layers of the upper air sounding.

        Parameters
        ----------
        layers : list
            The indexes of the layers.

        Returns
        -------
        out : tuple, yield
            The returned tuple contains four pieces of information on the analysed layer:

            * the evolution of the potential temperature;

            * the evolution of the wet bulb potential temperature;

            * the saturation at the bottom of the layer;

            * the saturation at the top of the layer.
        """
        for index in range(len(layers) - 1):
            pt_start = mpcalc.potential_temperature(
                self.data["press"][index], self.data["temp"][index]
            )
            pt_end = mpcalc.potential_temperature(
                self.data["press"][index + 1], self.data["temp"][index + 1]
            )

            wbpt_start = mpcalc.wet_bulb_potential_temperature(
                self.data["press"][index],
                self.data["temp"][index],
                self.data["dewpoint"][index],
            )
            wbpt_end = mpcalc.wet_bulb_potential_temperature(
                self.data["press"][index + 1],
                self.data["temp"][index + 1],
                self.data["dewpoint"][index + 1],
            )

            yield (
                (pt_end - pt_start) > 0,
                (wbpt_end - wbpt_start) > 0,
                (
                    self.data["temp"][index].magnitude
                    - self.data["dewpoint"][index].magnitude
                )
                < 0.2,
                (
                    self.data["temp"][index + 1].magnitude
                    - self.data["dewpoint"][index + 1].magnitude
                )
                < 0.2,
            )

    def show(self, layers: tuple = ()):
        """
        Plots and displays the upper air sounding on a Skew-T diagramm and a hodograph.

        Parameters
        ----------
        layers : tuple, optionnal
            By default: ``()``.
            The layers to be represented on the Skew-T diagramm.
        """
        fig = plt.figure(figsize=(18, 10))
        idx = mpcalc.resample_nn_1d(
            self.data["press"], np.arange(100, 1000, 25) * units.hPa
        )
        profile = mpcalc.parcel_profile(
            self.data["press"], self.data["temp"][0], self.data["dewpoint"][0]
        ).to("degC")

        skew = SkewT(fig, rect=(0.05, 0.05, 0.5, 0.90))
        skew.plot(self.data["press"], self.data["temp"], "r", lw=2, label="Température")
        skew.plot(
            self.data["press"],
            self.data["wb_temp"],
            "b",
            lw=2,
            label="Température du thermomètre mouillé",
        )
        skew.plot_barbs(
            pressure=self.data["press"][idx],
            u=self.data["wind_u"][idx],
            v=self.data["wind_v"][idx],
        )
        skew.plot(self.data["press"], profile, "k", lw=1)
        skew.shade_cin(
            self.data["press"],
            self.data["temp"],
            profile,
            self.data["dewpoint"],
            color="blue",
            alpha=0.3,
            label="CIN",
        )
        skew.shade_cape(
            self.data["press"],
            self.data["temp"],
            profile,
            color="red",
            alpha=0.3,
            label="CAPE",
        )
        if layers:
            skew.plot(
                layers[0],
                layers[1],
                "o",
                color="darkorange",
                label="Couches auto-détectées",
            )
        skew.plot_dry_adiabats(ls="solid", colors="forestgreen", alpha=0.75)
        skew.plot_moist_adiabats(ls="dashed", colors="forestgreen", alpha=0.75)
        skew.ax.set_xlabel("Température (°C)")
        skew.ax.set_ylabel("Pression (hPa)")

        hodo = Hodograph(plt.axes((0.45, 0.51, 0.44, 0.44)), component_range=50)
        hodo.add_grid(increment=10, ls="-", lw=1.5, alpha=0.75)
        hodo.add_grid(increment=5, ls="--", lw=1, alpha=0.75)
        hodo.plot_colormapped(
            self.data["wind_u"], self.data["wind_v"], c=self.data["press"], label="Vent"
        )
        hodo.ax.set_box_aspect(1)
        hodo.ax.set_xticks([])
        hodo.ax.set_yticks([])
        plt.xticks(np.arange(0, 0, 1))
        plt.yticks(np.arange(0, 0, 1))
        for i in range(10, 120, 10):
            hodo.ax.annotate(
                str(i),
                (i, 0),
                xytext=(0, 2),
                textcoords="offset pixels",
                clip_on=True,
                fontsize=10,
                weight="bold",
                alpha=0.3,
                zorder=0,
            )
            hodo.ax.annotate(
                str(i),
                (0, i),
                xytext=(0, 2),
                textcoords="offset pixels",
                clip_on=True,
                fontsize=10,
                weight="bold",
                alpha=0.3,
                zorder=0,
            )

        # hodo.ax.set_xlabel(r'Vitesse (Est, m$\cdot$s$^{-1}$)')
        # hodo.ax.set_ylabel(r'Vitesse (Nord, m$\cdot$s$^{-1}$)')

        # fig.patches.extend([plt.Rectangle(
        #         (0.56, 0.05), 0.39, 0.44,
        #         edgecolor='black',
        #         facecolor='white',
        #         lw=1,
        #         alpha=1,
        #         transform=fig.transFigure,
        #         figure=fig
        #     )])
        # # espace de 0.025
        # try:
        #     cape, cin = mpcalc.surface_based_cape_cin(
        #             self.data['press'],
        #             self.data['temp'],
        #             self.data['dewpoint']
        #         )
        #     cape = round(cape.magnitude, 0)
        #     cin = round(cin.magnitude, 0)
        # except ValueError:
        #     cape = cin = np.nan
        # plt.figtext(0.562, 0.47, 'Informations', fontsize=15, weight='bold')
        # plt.figtext(0.562, 0.445, rf'CAPE : {cape} J$\cdot$kg$^{{-1}}$', fontsize=15)
        # plt.figtext(0.562, 0.42, rf'CIN : {cin} J$\cdot$kg$^{{-1}}$', fontsize=15)

        skew.ax.legend(loc="upper left")
        hodo.ax.legend(loc="upper left")
        plt.show()

    def auto_layers(self, layer_size: int = 0, nb_layers: int = 10, show: bool = False):
        """
        This method attempts to find interesting layers in the upper air sounding and prints the
        characteristics of these layers.

        Parameters
        ----------
        layer_size : int, optionnal
            By default: automatic size.
            The size of each layers in termes of indexes.
        nb_layers : int, optionnal
            By default: ``10``.
            The maximum number of layers you want.
        show : bool, optionnal
            By default: ``False``.
            If set on ``True``, once the layers have been analyzed, it will plot the layers on the
            Skew-T diagramm.
        """

        def get_evolution(delta: float):
            if delta > 0:
                return "increase"
            return "decrease"

        if not layer_size:
            layer_size = self.nb_data // nb_layers

        layers = get_layers(
            layer_size,
            nb_layers,
            self.data["temp"],
            self.data["dewpoint"],
            self.data["p_temp"],
            self.data["wbp_temp"],
        )
        press = self.data["press"][layers].magnitude
        temp = self.data["temp"][layers].magnitude
        for index, info in enumerate(self.__layers_analysis(layers)):
            title = f"Layer n°{index + 1}"
            print(f"{title}\n" + len(title) * "-")

            print("Limits")
            print(f".. pressure    : {press[index]} hPa – {press[index + 1]} hPa")
            print(f".. temperature : {temp[index]}°C – {temp[index + 1]}°C")

            print("Information")
            print(f".. potential temperature          : {get_evolution(info[0])}")
            print(f".. wet bulb potential temperature : {get_evolution(info[1])}")
            print(f".. saturation base                : {info[2]}")
            print(f".. saturation top                 : {info[3]}")

            print()

        if show:
            self.show((press, temp))
