USER_INPUT = {
    'PROCESS_DATA': False,  # False: no preprocessing and transformation of coordinate system; True: transforming
    # coordinate system to another
    'CLASS_SELECTION': 20,  # 6 or 20 based on choosing hard classes
    'ZIPPED_DATA': True
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
    'SELECT_PNV_CLASS': 6,
    'SELECT_YEAR': 2050,
    'SELECT_RCP': ['rcp26', 'rcp45', 'rcp85'],
    'SELECT_AGG_LVL': 'country',
    'SELECT_ISO': ['big_10'],
    'REL_VAL_TOLERANCE': 0.9,
    'PAPER_FORMAT': True,
    'SAVE_FIGURE': True,
    'OUTPUT_NAME': 'test_test_output'
}
