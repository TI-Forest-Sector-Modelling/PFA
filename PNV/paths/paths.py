import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_RAW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw')
PREPROCESSED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'preprocessed')
OUTPUT_PATH = os.path.join(BASE_DIR, 'data', 'outputs')

# HILDA v2.0 data path (Winkler et al., 2025)
HILDAv2_DATA_2015_PATH = os.path.join(INPUT_RAW_DATA_PATH, 'hilda_plus_states_2015_GLOB-v2_wgs84.tif')
HILDAv2_DATA_2020_PATH = os.path.join(INPUT_RAW_DATA_PATH, 'hilda_plus_states_2020_GLOB-v2_wgs84.tif')

HILDAv2_DATA_2015_NEW_CRD_PATH = os.path.join(OUTPUT_PATH, 'hilda_plus_2015_v2_epsg8857.tif')
HILDAv2_DATA_2020_NEW_CRD_PATH = os.path.join(OUTPUT_PATH, 'hilda_plus_2020_v2_epsg8857.tif')

# HILDA v1.0 data path (Winkler et al., 2021)
HILDAv1_DATA_2015_PATH = os.path.join(INPUT_RAW_DATA_PATH, 'hilda_plus_2015_states_GLOB-v1-0_base-map_wgs84-nn.tif')

HILDAv1_DATA_2015_NEW_CRD_PATH = os.path.join(OUTPUT_PATH, 'hilda_plus_2015_v1_epsg8857.tif')
