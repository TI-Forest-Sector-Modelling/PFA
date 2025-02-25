import os
import pandas as pd
import numpy as np
import datetime as dt
import pickle
import pathlib
import os.path

import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from PNV.paths.paths import OUTPUT_PATH, INPUT_RAW_DATA_PATH
from PNV.user_input.default_parameters import TOOLBOX_INPUT
from PNV.src.base_logger import get_logger
from PNV.src.defines import PotentialNaturalVegetationArea, Coordinates


class PnvDataAnalysis:
    def __init__(self, user_input: dict):
        """
        Initialization of the class PnvDataAnalysis and read-in of input data.
        :param user_input: Dictionary of input parameters.
        """

        self.current_dt = dt.datetime.now().strftime("%Y%m%dT%H-%M-%S")
        self.logger = get_logger(user_path=None)

        self.selected_pnv_classes = user_input['SELECT_PNV_CLASS']
        self.selected_year = user_input['SELECT_YEAR']
        self.selected_rcp = user_input['SELECT_RCP']
        self.selected_agg_lvl = user_input['SELECT_AGG_LVL']
        self.selected_iso = user_input['SELECT_ISO']
        self.rel_val_tolerance = user_input['REL_VAL_TOLERANCE']

        self.save_figures = user_input['SAVE_FIGURE']

        self.input_folder = INPUT_RAW_DATA_PATH
        self.output_folder = OUTPUT_PATH
        self.output_name = user_input['OUTPUT_NAME']

        self.pnv_raw_data = self.readin_pnv_data()
        self.geo_data = self.readin_geo_data()
        self.fontsize = self.define_format(paper_format=user_input['PAPER_FORMAT'])
        self.color_palette = self.define_color_palette(selected_pnv_classes=user_input['SELECT_PNV_CLASS'])

        self.pnv_data_extrapolated = {}
        self.pnv_forest_data_raw = {}
        self.pnv_forest_data_extrapolated = {}

    def readin_pnv_data(self) -> pd.DataFrame:
        """
        Deserialize PNV data from pkl-files provided by the main application.
        :return: Deserialized pnv_data dataframe.
        """
        filename_path = max([f for f in pathlib.Path(
            os.path.abspath(OUTPUT_PATH)).glob(f'*_{self.selected_pnv_classes}_class_combined.pkl')],
                            key=os.path.getctime)
        self.logger.info(f"Readin PNV data from {filename_path}")
        with open(filename_path, "rb") as pkl_file:
            obj = pickle.load(pkl_file)
        return obj

    def readin_geo_data(self) -> pd.DataFrame:
        """
        Read-in additional geographic data.
        :return: geo_data dataframe.
        """
        self.logger.info(f"Readin geographic data from {self.input_folder}")
        src_filepath = os.path.join(self.input_folder, 'geo_data.csv')
        geo_data = pd.read_csv(src_filepath)

        return geo_data

    def define_format(self, paper_format: bool):
        """
        Defines a uniform format for all figures.
        :param paper_format: Boolean controlling if the font size is set for publications (True) or presentations
         (False).
        :return: Dictionary with formats.
        """
        if paper_format:
            fontsize = {"title": 10, "ticks": 9, "labels": 9}
        else:
            fontsize = {"title": 13, "ticks": 12, "labels": 12}

        return fontsize

    def define_color_palette(self, selected_pnv_classes: int):
        """
        Defines the color palette for all figures based on the number of selected classes.
        :param selected_pnv_classes: Number of selected classes.
        :return: Color palette.
        """
        if self.selected_pnv_classes == 6:
            color_palette = sns.color_palette("Accent")
        else:
            color_palette = plt.get_cmap('Spectral')(np.linspace(0, 1.5, self.selected_pnv_classes))
        return color_palette

    def split_pnv_data(self):
        """
        PNV data are split regarding the RCP scenarios and saved as a dictionary.
        :return: Dictionary of pnv_data dataframes for each RCP scenario.
        """
        self.logger.info(f"Split PNV data")
        splitted_data = self.pnv_raw_data.copy()
        scenario_data = [x.split(".")[-1] for x in self.pnv_raw_data["Sheet Name"]]
        splitted_data["scenario"] = [x.split("_")[0] for x in scenario_data]
        splitted_data["period"] = [int(x.split("_")[-1][:4]) for x in scenario_data]
        index_hist_data = splitted_data[splitted_data["scenario"] == "hcl"].index
        splitted_data.loc[index_hist_data, "scenario"] = "history"

        pnv_data_dict = {}

        for scenario in splitted_data["scenario"].unique():
            selected_scenario = splitted_data[splitted_data["scenario"] == scenario].reset_index(drop=True)
            pnv_data_dict[scenario] = selected_scenario.copy()

        return pnv_data_dict

    def reformate_pnv_data(self) -> pd.DataFrame:
        """
        Steps for reformating PNV data, including conversion and data curration steps.
        :return: Reformated PNV dataframe.
        """
        self.logger.info(f"Reformate PNV data")
        self.pnv_raw_data["total_area_ha"] = self.pnv_raw_data["Total Area (km^2)"] * 100
        self.pnv_raw_data["total_area_tsd_ha"] = self.pnv_raw_data["total_area_ha"] / 1000
        kosovo_index = self.pnv_raw_data[self.pnv_raw_data["ISO"] == "-99"].index
        self.pnv_raw_data.loc[kosovo_index, "ISO"] = "XKX"
        pnv_classes = self.pnv_raw_data.columns[3: 3 + self.selected_pnv_classes]

        pnv_raw_data_reformated = pd.DataFrame()
        info_data = self.pnv_raw_data[["country", "ISO", "Sheet Name", "total_area_ha", "total_area_tsd_ha"]].copy()
        info_data = info_data.merge(self.geo_data, left_on="ISO", right_on="ISO", how="left")
        for pnv_class in pnv_classes:
            tmp_data = pd.DataFrame()
            tmp_data["pnv_class"] = pd.DataFrame([pnv_class] * len(info_data))
            tmp_data["area_tsd_ha"] = self.pnv_raw_data[pnv_class] / 10  # Conversion km² to tsd_ha

            tmp_data = pd.concat([info_data, tmp_data], axis=1)
            pnv_raw_data_reformated = pd.concat([pnv_raw_data_reformated, tmp_data], axis=0)

        return pnv_raw_data_reformated

    def pnv_data_extrapolation(self):
        """
        Extrapolates PNV data between provided time points (1979-2013, 2040-2060, 2061-2080). Within the provided time
        periods, PNV are assumed to be constant in line with Bonnanella et al. (2023).
        :return: Dictionary of extrapolated pnv_data dataframes for each RCP scenario.
        """
        self.logger.info(f"Extrapolate PNV data")
        historic_data = self.pnv_data_dict["history"].reset_index(drop=True)
        for key in self.pnv_data_dict.keys():
            if "rcp" in key:
                pnv_rcp = self.pnv_data_dict[key]
                pnv_rcp_extrapolation = pnv_rcp[["ISO", "scenario", "pnv_class", "continents", "fao_regions"
                                                 ]].drop_duplicates().reset_index(drop=True)
                for period in pnv_rcp["period"].unique():
                    pnv_rcp_period = pnv_rcp[pnv_rcp["period"] == period].reset_index(drop=True)
                    period_end = period
                    data_end = pnv_rcp_period["area_tsd_ha"]

                    if period == 2040:
                        period_start = 2013
                        data_start = historic_data["area_tsd_ha"]
                        period_len = period_end - period_start
                        yearly_dev = (data_end - data_start) / period_len
                        for year in range(period_start, period_end):  # + 1 to take 2040
                            if (year == 2013) or (year == 2040) or (year == 2061):
                                pnv_rcp_year = pd.DataFrame(data_start).rename(columns={"area_tsd_ha": year})
                            else:
                                pnv_rcp_year = pnv_rcp_extrapolation[year - 1] + yearly_dev
                                pnv_rcp_year = pd.DataFrame(pnv_rcp_year).rename(columns={0: year})

                            pnv_rcp_extrapolation = pd.concat([pnv_rcp_extrapolation, pnv_rcp_year], axis=1)

                    if period == 2061:
                        period_start = 2040
                        period_end = 2060
                        data_start = pnv_rcp[pnv_rcp["period"] == period_start]["area_tsd_ha"].reset_index(drop=True)

                        for year in range(period_start, period_end + 1):
                                pnv_rcp_year = pd.DataFrame(data_start).rename(columns={"area_tsd_ha": year})
                                pnv_rcp_extrapolation = pd.concat([pnv_rcp_extrapolation, pnv_rcp_year], axis=1)

                        period_start = 2061
                        period_end = 2080

                        data_start = pnv_rcp[pnv_rcp["period"] == period_start]["area_tsd_ha"].reset_index(drop=True)

                        for year in range(period_start, period_end + 1):
                            pnv_rcp_year = pd.DataFrame(data_start).rename(columns={"area_tsd_ha": year})
                            pnv_rcp_extrapolation = pd.concat([pnv_rcp_extrapolation, pnv_rcp_year], axis=1)

                pnv_rcp_extrapolation = pnv_rcp_extrapolation.drop_duplicates().reset_index(drop=True)

                self.pnv_data_extrapolated[f"{key}"] = pnv_rcp_extrapolation

    def land_surface_validation(self, rel_tolerance):
        """
        Validates processed data with land surface data from WDI for the year 2013. Countries without WDI land surface
        data are not validated (ESH, FLK, ATF, TWN, CYN, XKX).
        :param rel_tolerance: Relative tolerance for the validation when comparing processed data with land surface data
        """
        self.logger.info(f"Validation of processed data using WDI land surface data")
        validation_data = self.geo_data[["ISO", "WDI_land_surface_km2"]]

        for key in self.pnv_data_extrapolated.keys():
            data_to_validate = self.pnv_data_extrapolated[key]

            for year in [2013, 2040, 2080]:
                data_to_validate_year = data_to_validate[["ISO", "scenario", "pnv_class", year]]
                data_to_validate_year = data_to_validate_year.groupby(["ISO", "scenario"])[year].sum().reset_index()
                data_to_validate_year[year] = data_to_validate_year[year] * 10  # Conversion tsd_ha to km²
                data_to_validate_year = data_to_validate_year.merge(validation_data, left_on="ISO", right_on="ISO",
                                                                    how="left")
                data_to_validate_year = data_to_validate_year.dropna(axis=0, how="any").reset_index(drop=True)

                validation_result = np.allclose(np.array(data_to_validate_year[year], dtype=float),
                                                np.array(data_to_validate_year["WDI_land_surface_km2"], dtype=float),
                                                rtol=rel_tolerance)

                if not validation_result:
                    validation_result_index = np.isclose(np.array(data_to_validate_year[year], dtype=float),
                                                         np.array(data_to_validate_year["WDI_land_surface_km2"],
                                                                  dtype=float),
                                                         rtol=rel_tolerance)
                    validation_result_index = pd.DataFrame(validation_result_index)
                    validation_result_index = validation_result_index[validation_result_index[0] == False].index
                    iso_failed_validation = data_to_validate_year.loc[validation_result_index]["ISO"].unique()
                    self.logger.info(f"Validation failed for scenario {key} in {year} for {len(iso_failed_validation):}"
                                     f" countries")
                    self.logger.info(f"{iso_failed_validation}")

                if validation_result:
                    self.logger.info(f"Validation succeeded for scenario {key} in {year} for all countries")

    def filter_forest_pnv_data(self):
        """
        Filters out and saves PNV data of forest-related PNV classes in separate dictionaries.
        :return: Dictionaries with PNV data of forest-related PNV classes.
        """
        self.logger.info(f"Filter forest-related classes from NVP data")
        if self.selected_pnv_classes == 6:
            forest_classes = PotentialNaturalVegetationArea.forest_classes_6.value
            forest_classes = list(forest_classes.values())
        if self.selected_pnv_classes == 20:
            forest_classes = PotentialNaturalVegetationArea.forest_classes_20.value
            forest_classes = list(forest_classes.values())

        for key in self.pnv_data_dict.keys():
            tmp_data = self.pnv_data_dict[key].copy()
            tmp_data = tmp_data[[x in forest_classes for x in tmp_data["pnv_class"]]].reset_index(drop=True)

            self.pnv_forest_data_raw[key] = tmp_data

        for key in self.pnv_data_extrapolated.keys():
            tmp_data = self.pnv_data_extrapolated[key].copy()
            tmp_data = tmp_data[[x in forest_classes for x in tmp_data["pnv_class"]]].reset_index(drop=True)

            self.pnv_forest_data_extrapolated[key] = tmp_data

    def preprocess_pnv_data(self):
        """
        Processing steps to prepare PNV data for calculations.
        """
        self.logger.info(f"Process PNV data")
        self.pnv_raw_data = self.reformate_pnv_data()
        self.pnv_data_dict = self.split_pnv_data()
        self.pnv_data_extrapolation()
        self.land_surface_validation(rel_tolerance=self.rel_val_tolerance)
        self.filter_forest_pnv_data()

    def build_geolocalized_subfig(self, mapx: float, mapy: float, ax: int, width: float, data: pd.DataFrame, title: str,
                                  y_max: float, fig_option: str, bar_plot_col: int, fontsize: dict):
        """
        Builds sub-figures within a larger map based on user inputs related to the geolocalization.
        :param mapx: Longitude of the sub-figure's origin.
        :param mapy: Latitude of the sub-figure's origin.
        :param ax: Current figure axes.
        :param width: Width of the sub-figure.
        :param data: Plotted data in the sub-figure.
        :param title: Title of the sub-figure.
        :param y_max: Maximal value of the y-axis.
        :param fig_option: Chosen figure option by the user.
        :param bar_plot_col: Year of the data that is plotted.
        :param fontsize: Font size used for the sub-figure's text.
        """
        ax_h = inset_axes(ax, width=width,
                          height=width,
                          loc=3,
                          bbox_to_anchor=(mapx, mapy),
                          bbox_transform=ax.transData,
                          borderpad=0,
                          axes_kwargs={'alpha': 0.35, 'visible': True})
        if fig_option == 'bar_chart':
            if len(self.selected_rcp) > 1:
                # Barchart for more than one RCP
                scenario = tuple(data["scenario"])
                pnv_class = {}
                for col in data.columns[2:]:
                    pnv_class[col] = np.array(data[col])
                width = 0.5
                bottom = np.zeros(len(scenario))
                color_runner = 0

                for boolean, pnv in pnv_class.items():
                    ax_h.bar(scenario, pnv, width, label=boolean, bottom=bottom,
                             color=self.color_palette[color_runner])
                    bottom = [bottom[x] + pnv[x] for x in range(0, len(scenario))]
                    color_runner += 1
                ax_h.set_xticks(list(data["scenario"]))
                ax_h.set_xticklabels(list(data["scenario"]), rotation=45, ha="right")
            else:
                # Barchart for one RCP
                sns.barplot(data=data, hue="pnv_class", y=int(bar_plot_col), palette=self.color_palette, ax=ax_h, capsize=.2,
                            linewidth=1, edgecolor="#04253a", legend=False)
                ax_h.set_xlabel('')
                ax_h.set_ylabel('')
                ax_h.set_xticks(ticks=[])
            ax_h.set_ylim([0, y_max + (0.10 * y_max)])

            ax_h.tick_params(axis='y', which='major', labelsize=fontsize['ticks'])

            ax_h.patch.set_alpha(0.75)
            ax_h.set_facecolor('white')
            ax_h.set_title(title, x=0.15, y=1.05, pad=-14, fontsize=fontsize['title'], fontweight='bold')

        if fig_option == 'pie_chart':

            ax_h.pie(x=data["pnv_share"], colors=sns.color_palette('Accent'),
                     wedgeprops={"linewidth": 1, "edgecolor": "white", "alpha": 1},
                     radius=data["rescaled_data"][0])
            ax_h.patch.set_alpha(0.75)
            ax_h.set_facecolor('white')

            if data["rescaled_data"][0] > 1.25:
                x_pos = -0.15
                y_pos = data["rescaled_data"][0] * 0.8
            elif data["rescaled_data"][0] < 0.75:
                x_pos = 0.20
                y_pos = data["rescaled_data"][0] * 1.3
            else:
                x_pos = 0.15
                y_pos = 1.05

            ax_h.set_title(title, x=x_pos, y=y_pos, pad=-14, fontsize=fontsize['title'],
                           fontweight='bold')

        return ax_h

    def pnv_bar_plot(self, plot_option: str, aggregate_forest: bool):
        """
        Generates a barplot of selected PNV data with different visualization options.
        :param plot_option: Flag to plot absolute forest-related PNV areas [tsd ha] (= "abs") or relative forest
        covers [%] (= "rel").
        :param aggregate_forest: Flag to plot summed forest-related PNV classes (= True) or separate forest-related PNV
        classes (= False).
        """
        self.logger.info(f"Generate barplot of PNV data for {self.selected_rcp} in {self.selected_year}")
        fontsize = self.fontsize
        total_area = self.pnv_data_dict['history'][["ISO", "continents", "fao_regions", "total_area_tsd_ha"
                                                    ]].drop_duplicates().reset_index(drop=True)
        fig_data = pd.DataFrame()

        for key in self.pnv_forest_data_extrapolated.keys():
            if key in self.selected_rcp:
                fig_data = pd.concat([fig_data, self.pnv_forest_data_extrapolated[key]], axis=0)

        fig_data = fig_data[["ISO", "scenario", "pnv_class", "continents", "fao_regions", self.selected_year]]

        if self.selected_agg_lvl == "country":
            self.selected_agg_lvl = "ISO"
            fig_data = fig_data[[self.selected_agg_lvl, "continents", "scenario", "pnv_class", self.selected_year]]
            if all(["big_" in x for x in self.selected_iso]):
                n_selected = int(self.selected_iso[0].split('_')[1])
                selected_iso = self.pnv_forest_data_raw['history'].groupby(["ISO"])["area_tsd_ha"].sum().reset_index()
                selected_iso["area_tsd_ha"] = pd.to_numeric(selected_iso["area_tsd_ha"], errors='coerce')
                selected_iso = list(selected_iso.nlargest(n_selected, "area_tsd_ha")[self.selected_agg_lvl])
                self.selected_iso = selected_iso

            if all([x in total_area["continents"].unique() for x in self.selected_iso]):
                selected_iso = list(fig_data[[x in self.selected_iso for x in fig_data["continents"]]]["ISO"].unique())
                self.selected_iso = selected_iso

            fig_data = fig_data[[x in self.selected_iso for x in fig_data["ISO"]]].reset_index(drop=True)
            total_area = total_area[[x in self.selected_iso for x in total_area["ISO"]]].reset_index(drop=True)
        else:  # if selected_agg_lvl == continents or fao_regions
            fig_data = fig_data[[self.selected_agg_lvl, "scenario", "pnv_class", self.selected_year]]
            total_area = total_area.groupby([self.selected_agg_lvl])["total_area_tsd_ha"].sum().reset_index()

        if plot_option == "rel":
            if aggregate_forest:
                fig_data = fig_data.groupby([self.selected_agg_lvl, "scenario"])[self.selected_year].sum().reset_index()
                fig_data = fig_data.merge(total_area, left_on=self.selected_agg_lvl, right_on=self.selected_agg_lvl,
                                          how="left")
                fig_data["forest_cover"] = (fig_data[self.selected_year] / fig_data["total_area_tsd_ha"]) * 100
            else:
                fig_data = fig_data.groupby([
                    self.selected_agg_lvl, "scenario", "pnv_class"])[self.selected_year].sum().reset_index()
                fig_data_new = fig_data[[self.selected_agg_lvl, "scenario"]].copy().drop_duplicates().reset_index(drop=True)
                for pnv_class in fig_data["pnv_class"].unique():
                    tmp_data = fig_data[fig_data["pnv_class"] == pnv_class][[self.selected_agg_lvl, self.selected_year
                                                                             ]].reset_index(drop=True)
                    tmp_data = tmp_data.merge(total_area, left_on=self.selected_agg_lvl, right_on=self.selected_agg_lvl,
                                              how="left")
                    tmp_data["forest_cover"] = (tmp_data[self.selected_year] / tmp_data["total_area_tsd_ha"]) * 100
                    tmp_data = pd.DataFrame(tmp_data["forest_cover"]).rename(columns={"forest_cover": pnv_class}
                                                                             ).reset_index(drop=True)
                    fig_data_new = pd.concat([fig_data_new, tmp_data], axis=1)
                fig_data = fig_data_new

            x_var = "forest_cover"
        else:
            x_var = self.selected_year
            if aggregate_forest:
                fig_data = fig_data.groupby([self.selected_agg_lvl, "scenario"])[self.selected_year].sum().reset_index()
            else:
                fig_data = fig_data.groupby([self.selected_agg_lvl, "scenario", "pnv_class"
                                             ])[self.selected_year].sum().reset_index()

                fig_data_new = fig_data[[self.selected_agg_lvl, "scenario"
                                         ]].copy().drop_duplicates().reset_index(drop=True)
                for pnv_class in fig_data["pnv_class"].unique():
                    tmp_data = pd.DataFrame(fig_data[fig_data["pnv_class"] == pnv_class][self.selected_year]
                                            ).rename(columns={self.selected_year: pnv_class}).reset_index(drop=True)
                    fig_data_new = pd.concat([fig_data_new, tmp_data], axis=1)
                fig_data = fig_data_new

        Agg_position = []
        agg_lvl_len = len(fig_data[self.selected_agg_lvl].unique())
        for Agg in range(0, agg_lvl_len):
            Agg_position.append(1)

        # Draw barplot
        sns.set_theme('paper')
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 10))

        if aggregate_forest:
            sns.barplot(data=fig_data, x=x_var, y=self.selected_agg_lvl, hue="scenario", orient="h", ax=ax,
                        palette=self.color_palette)
            if plot_option == "rel":
                ax.set(ylabel=self.selected_agg_lvl,
                       xlabel=f"Area share of forest-related PNV [%] in {self.selected_year}")
            else:
                ax.set(ylabel=self.selected_agg_lvl,
                       xlabel=f"Area of forest-related PNV [Tsd ha] in {self.selected_year}")
        else:
            fig_data["y_var"] = fig_data[self.selected_agg_lvl] + "_" + fig_data["scenario"]
            fig_data.set_index(["y_var"]).plot.barh(stacked=True, color=sns.color_palette(self.color_palette), ax=ax)

            if plot_option == "rel":
                ax.set(ylabel=self.selected_agg_lvl,
                       xlabel=f"Area share [%] in {self.selected_year}")
            else:
                ax.set(ylabel=self.selected_agg_lvl,
                       xlabel=f"Area [Tsd ha] in {self.selected_year}")

        # Draw lines to sperate plotted aggregates
        x = [ax.get_position().x0 - .1, ax.get_position().x0 + ax.get_position().width]
        y_width = ax.get_position().y1 - ax.get_position().y0
        y0 = ax.get_position().y0 + ax.get_position().height

        text_position_list = []
        for y1 in Agg_position[:-1]:
            y0_prev = y0.copy()
            y0 -= y1 * (y_width / len(fig_data[self.selected_agg_lvl].unique()))
            text_position_list.append(y0_prev - ((y0_prev - y0) / 2))
            y_coord = [y0, y0]
            line = Line2D(x, y_coord, lw=1, color='grey', linestyle="--", alpha=0.25)
            fig.add_artist(line)

        if plot_option == "rel":
            fig_title = "Rel_forest_PNV_cover"
        else:
            fig_title = "Abs_forest_PNV_areas"

        ax.set_title(f"{fig_title}_{self.selected_agg_lvl}_{'_'.join(self.selected_rcp)}_{self.selected_year}")

        if self.selected_pnv_classes == 6:
            ax.legend(loc=1, title='PNV classes', title_fontsize=fontsize['title'], fontsize=fontsize['labels'])

        else:
            ax.legend(loc=8, title='PNV classes', title_fontsize=fontsize['title'], fontsize=fontsize['labels'],
                      bbox_to_anchor=(0.5, - 0.22), ncol=3)

        if self.save_figures:
            self.logger.info(f"Save barplot")
            plt.savefig(f"{self.output_folder}\\{self.current_dt}_bar_plot_{self.output_name}.png",
                        dpi=300, bbox_inches='tight')

    def pnv_world_map(self, fig_option: str, winkel_reproject: bool, dissolve_map_regions: bool):
        """
        Generates a world map with selected PNV data with different visualisation options.
        :param fig_option: Flag to select the figure type ("bar_chart" or "pie_chart").
        :param winkel_reproject: Flag to activate the reprojection to Winkel triple projection
        :param dissolve_map_regions: Flag to activate the dissolution of country borders.
        """
        self.logger.info(f"Generate world map with PNV data for {self.selected_rcp} in {self.selected_year}")
        fontsize = self.fontsize
        total_area = self.pnv_data_dict['history'][[
            "ISO", "continents", "fao_regions", "total_area_tsd_ha"]].drop_duplicates().reset_index(drop=True)
        total_area_agg_lvl = total_area.groupby([self.selected_agg_lvl])["total_area_tsd_ha"].sum().reset_index()
        total_area_agg_lvl = total_area_agg_lvl.rename(columns={"total_area_tsd_ha": "total_area_region_tsd_ha"})
        fig_data = pd.DataFrame()

        for key in self.pnv_forest_data_extrapolated.keys():
            if key in self.selected_rcp:
                fig_data = pd.concat([fig_data, self.pnv_forest_data_extrapolated[key]], axis=0)

        fig_data = fig_data[["ISO", "scenario", "pnv_class", "continents", "fao_regions", self.selected_year]]

        # Map background data (forest cover)
        agg_lvl_back = self.selected_agg_lvl
        if "ISO" in agg_lvl_back:
            fig_data_back = fig_data.groupby([agg_lvl_back, "scenario"]
                                             )[self.selected_year].sum().reset_index()
        else:
            fig_data_back = fig_data.groupby(["ISO", agg_lvl_back, "scenario"])[self.selected_year].sum().reset_index()
        fig_data_back = fig_data_back.merge(total_area[["ISO", "total_area_tsd_ha"]], left_on="ISO",
                                            right_on="ISO", how="left")

        # weights for each country in each region
        fig_data_back = fig_data_back.merge(total_area_agg_lvl, left_on=agg_lvl_back,
                                            right_on=agg_lvl_back, how="left")
        fig_data_back = fig_data_back[fig_data_back["total_area_tsd_ha"] > 0].reset_index(drop=True)
        fig_data_back["forest_cover"] = (fig_data_back[self.selected_year] / fig_data_back["total_area_tsd_ha"]) * 100

        # Map foreground data (forest pnv class shares or forest pnv area)
        if "ISO" in self.selected_agg_lvl:
            agg_lvl_fore = "continents"
        else:
            agg_lvl_fore = self.selected_agg_lvl

        fig_data_fore = fig_data.groupby([agg_lvl_fore, "scenario", "pnv_class"]
                                         )[self.selected_year].sum().reset_index()
        fig_data_fore_summed = fig_data.groupby([agg_lvl_fore, "scenario"])[self.selected_year].sum().reset_index()
        fig_data_fore_summed = fig_data_fore_summed.rename(columns={self.selected_year: f"{self.selected_year}_sum"})
        fig_data_fore = fig_data_fore.merge(fig_data_fore_summed, left_on=[agg_lvl_fore, "scenario"],
                                            right_on=[agg_lvl_fore, "scenario"], how="left")
        fig_data_fore["pnv_share"] = fig_data_fore[self.selected_year] / fig_data_fore[f"{self.selected_year}_sum"]

        # Map background
        path_to_data = gpd.datasets.get_path('naturalearth_lowres')
        world = gpd.read_file(path_to_data)
        world = world[world['name'] != 'Antarctica']
        if winkel_reproject:
            world = world.to_crs("+proj=wintri")
        sns.set_theme('paper')
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 22))
        cmap = "YlGn"

        fig_data_back = fig_data_back[fig_data_back["scenario"] == self.selected_rcp[0]].reset_index(drop=True)
        fig_data_back = world.merge(fig_data_back, left_on='iso_a3', right_on='ISO', how='left')
        if dissolve_map_regions:
            fig_data_back = fig_data_back[[agg_lvl_back, "geometry", "forest_cover"]]
            fig_data_back = fig_data_back[fig_data_back[agg_lvl_back] != 0].reset_index(drop=True)
            fig_data_back = fig_data_back.dissolve(by=agg_lvl_back, aggfunc="mean")

        fig_data_back.plot(column="forest_cover", ax=ax, cmap=cmap, edgecolor="#04253a")
        # colorbar
        divider = make_axes_locatable(ax)  # for legend-colorbar
        cax = divider.append_axes("right", size="5%", pad=0.1)  # for legend-colorbar
        ax.axes.xaxis.set_visible(False)  # Set x-axis-labels invisible
        ax.axes.yaxis.set_visible(False)
        cb_label = f"forest cover [%] in {self.selected_year} for {self.selected_rcp[0]}"
        cb = fig.colorbar(ax.get_children()[0], cax=cax, orientation='vertical')
        cb.ax.tick_params(axis='both', labelsize=fontsize['ticks'])
        cb.set_label(label=cb_label, size=fontsize['labels'])
        cb.formatter.set_useMathText(True)
        cb.outline.set_edgecolor('black')

        # Rescaling for pie charts
        interval_min = 0.5
        interval_max = 1.5
        forest_area_data = np.array([fig_data_fore[f"{self.selected_year}_sum"]])
        rescaled_data = ((forest_area_data - np.min(forest_area_data)) /
                         (np.max(forest_area_data) - np.min(forest_area_data)) *
                         (interval_max - interval_min) + interval_min)
        fig_data_fore["rescaled_data"] = pd.DataFrame(rescaled_data.T)

        # Transformation for barplot
        fig_data_fore_new = fig_data_fore[[agg_lvl_fore, "scenario"]].drop_duplicates().reset_index(drop=True)
        for pnv_class in fig_data_fore["pnv_class"].unique():
            tmp_data = pd.DataFrame(
                fig_data_fore[fig_data_fore["pnv_class"] == pnv_class][
                    self.selected_year]).rename(columns={self.selected_year: pnv_class}).reset_index(drop=True)
            fig_data_fore_new = pd.concat([fig_data_fore_new, tmp_data], axis=1)

        if agg_lvl_fore == 'fao_regions':
            if winkel_reproject:
                lon_lat_dict_new = Coordinates.coord_fao_reg_winkel_proj.value
            else:
                lon_lat_dict_new = Coordinates.coord_fao_reg_default_proj.value
        if agg_lvl_fore == 'continents':
            if winkel_reproject:
                lon_lat_dict_new = Coordinates.coord_continents_winkel_proj.value
            else:
                lon_lat_dict_new = Coordinates.coord_continents_default_proj.value

        y_axis_max = max(fig_data_fore[self.selected_year])

        title = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']
        for agg_region, region_title in zip(fig_data_fore_new[agg_lvl_fore].unique(), title):
            if len(self.selected_rcp) > 1:
                region_data = fig_data_fore_new[
                    fig_data_fore_new[agg_lvl_fore] == agg_region].reset_index(drop=True)
            else:
                region_data = fig_data_fore[
                    fig_data_fore[agg_lvl_fore] == agg_region].reset_index(drop=True)

            lat, lon = lon_lat_dict_new[agg_region][0], lon_lat_dict_new[agg_region][1]

            bax = self.build_geolocalized_subfig(mapx=lon, mapy=lat, ax=ax, width=0.85, data=region_data,
                                                 bar_plot_col=f"{self.selected_year}", title=region_title,
                                                 y_max=y_axis_max, fig_option=fig_option, fontsize=fontsize)
        # Set legend
        patches = []
        patch_runner = 0
        for pnv_class in fig_data_fore["pnv_class"].unique():
            patch = mpatches.Patch(color=self.color_palette[patch_runner], label=pnv_class)
            patches.append(patch)
            patch_runner += 1

        if self.selected_pnv_classes == 6:
            ax.legend(handles=patches, loc=8, title='PNV classes', title_fontsize=fontsize['title'],
                      fontsize=fontsize['labels'], bbox_to_anchor=(0.5, - 0.2))

        else:
            ax.legend(handles=patches, loc=8, title='PNV classes', title_fontsize=fontsize['title'],
                      fontsize=fontsize['labels'], bbox_to_anchor=(0.5, - 0.3), ncol=3)
        # todo short legend text
        ax.set_title(f"PNV_world_map_{agg_lvl_fore}_{'_'.join(self.selected_rcp)}_{self.selected_year}")
        if self.save_figures:
            self.logger.info(f"Save world map")
            plt.savefig(
                f"{self.output_folder}\\{self.current_dt}_world_map_{self.output_name}.png",
                dpi=300, bbox_inches='tight')

    def toolbox_plot(self):
        """
        Bundles and executes all functions to process and visualize the data based on the user input.
        """

        self.preprocess_pnv_data()

        self.pnv_bar_plot(plot_option='rel',  # options: ['abs', 'rel']
                          aggregate_forest=False,
                          )

        self.pnv_world_map(fig_option='bar_chart',  # options: ['pie_chart', 'bar_chart']
                           winkel_reproject=False,
                           dissolve_map_regions=True
                           )
        self.logger.info(f"PNV data analysis completed")


if __name__ == "__main__":

    pnv_analysis = PnvDataAnalysis(user_input=TOOLBOX_INPUT)

    pnv_analysis.preprocess_pnv_data()

    pnv_analysis.pnv_bar_plot(plot_option='rel',  # options: ['abs', 'rel']
                              aggregate_forest=False  # options: True or False
                              )

    pnv_analysis.pnv_world_map(fig_option='bar_chart',  # options: ['pie_chart', 'bar_chart']
                               winkel_reproject=False,
                               dissolve_map_regions=True
                               )
    pnv_analysis.logger.info(f"PNV data analysis completed")

