from typing import Union
import os
from pathlib import Path
import datetime as dt
import logging
from PNV.paths.paths import OUTPUT_PATH


def get_logger(user_path: Union[str, Path, None]):
    """
    Set up and configure a logger for logging messages.
    :param user_path: Information to log
    :return: logged message
    """
    current_dt = dt.datetime.now().strftime("%Y%m%d")
    filename = rf"{current_dt}_PNV_processing.log"

    if user_path is None:
        filepath = os.path.join(OUTPUT_PATH, filename)
    else:
        filepath = os.path.join(user_path, "output", filename)
    if not os.path.exists(filepath):
        os.makedirs(Path(filepath).parent, exist_ok=True)

    Logger = logging.getLogger("PNV-Processing")
    if not Logger.hasHandlers():
        Logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(lineno)s: %(message)s',
            '%d.%m.%y %H:%M:%S'
        )
        handler = logging.FileHandler(filepath, 'a+')
        handler.setFormatter(formatter)
        Logger.addHandler(handler)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(name)-10s: %(levelname)-10s %(message)s')
        console.setFormatter(console_formatter)
        Logger.addHandler(console)
    return Logger
