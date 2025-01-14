import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_RAW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'raw')
PREPROCESSED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'preprocessed')
OUTPUT_PATH = os.path.join(BASE_DIR, 'data', 'outputs')