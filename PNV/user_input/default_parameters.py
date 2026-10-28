from PNV.src.defines import ParamNames

USER_INPUT = {
    ParamNames.process_data.value: False,  # False: no preprocessing and transformation of coordinate system; True: transforming
    # coordinate system to another
    ParamNames.class_selection.value: 6,  # 6 or 20 based on choosing hard classes
    ParamNames.plot_maps.value: True,
    ParamNames.plot_downscale_factor.value: 100,  # Factor to downscale plotted world maps (no downscale == 1)
    ParamNames.zipped_data.value: True,
    ParamNames.merge_agri_data.value: True,
    ParamNames.year_agri_data.value: 2020,  # Options: 2015, 2020 (From HILDA+ v2.0 Winkler et al. 2025)
    ParamNames.generate_fig.value: True,
    ParamNames.generate_gif.value: True,
    ParamNames.calc_gain_loss.value: False
}

SRC_CRS = 'EPSG:4326'
DST_CRS = 'EPSG:8857'

"""
Information about TOOLBOX_INPUT:
'SELECT_PNV_CLASS': Number of biome classes selected (selection options: 6 or 20)
'SELECT_YEAR': Selected year for which data will be plotted (selection options: 2013 to 2080) 
'SELECT_RCP': Selected rcp for which data will be plotted (selection options: ['rcp26', 'rcp45', 'rcp85']) 
'SELECT_AGG_LVL': Selected aggregation level which will be used for spatial aggregation
(selection options: ['continents', 'fao_regions', 'country'], if 'continents' or 'fao_regions' are selected, the option
 'SELECT_ISO' will not be considered)
'SELECT_ISO': Selected country ISO code which data will be plotted
(selection options: ['any ISO3-list', 'big_n', 'continent name']. 
    - 'any ISO3-list' option shows all countries in the list of ISO3 codes (e.g., ['GER', 'FRA', 'SWE'] 
    - 'big_n' option shows the countries with n-largest forest area (e.g., ['big_10'] or ['big_5'])
    - 'continent name' option shows all countries within the selected continent (e.g. ['South America'] or ['Asia'])
'REL_VAL_TOLERANCE': Relative tolerance applied for the validation of aggregated data with land surface data from WDI 
'PAPER_FORMAT': Controls the fontsize in figures
'SAVE_FIGURE': Controls if the figures are saved in the output directory
'OUTPUT_NAME': Name of output file
"""

TOOLBOX_INPUT = {
    ParamNames.class_selection.value: 20,
    ParamNames.merge_agri_data.value: True,
    ParamNames.select_year.value: 2050,
    ParamNames.select_rcp.value: ['rcp26', 'rcp45', 'rcp85'],
    ParamNames.select_agg_lvl.value: 'continents',
    ParamNames.select_iso.value: ['big_10'],
    ParamNames.rel_val_tolerance.value: 0.3,
    ParamNames.paper_format.value: True,
    ParamNames.save_figure.value: True,
    ParamNames.output_name.value: '_6k'
}
