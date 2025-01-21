import matplotlib.pyplot as plt
import rasterio
import numpy as np
import matplotlib.colors as mcolors
import geopandas as gpd
import os
import glob
import pandas as pd
import datetime as dt

from rasterio.mask import mask
from shapely.geometry import mapping
from tqdm import tqdm

from PNV.src.datamanager import colors_6, labels_6, colors_20, labels_20
from PNV.src.datapreprocces import process_all_files
from PNV.user_input.default_parameters import USER_INPUT, TOOLBOX_INPUT, SRC_CRS, DST_CRS
from PNV.src.base_logger import get_logger
from PNV.paths.paths import INPUT_RAW_DATA_PATH, PREPROCESSED_DATA_PATH, OUTPUT_PATH


class ProcessingArea:
    def __init__(self):
        """
        Initialization of the class ProcessingArea. Read in and preprocess input file to calculate the country-specific
        area for different classes (IUCN and biomes).
        """
        self.logger = get_logger(user_path=None)
        self.time_stamp = dt.datetime.now().strftime("%Y%m%dT%H-%M-%S")
        self.class_selection = USER_INPUT['CLASS_SELECTION']

        if self.class_selection not in [6, 20]:
            raise ValueError("Invalid class selection. Must be 6 or 20.")
        self.logger.info(f"Class selection set to: {self.class_selection}")

        if USER_INPUT['PROCESS_DATA']:
            self.logger.info(f"Processing data...")
            process_all_files(INPUT_RAW_DATA_PATH, PREPROCESSED_DATA_PATH, SRC_CRS, DST_CRS)
            self.logger.info(f"Data processing complete.")

        self.tif_files = self.filter_tif_files_by_selection()
        self.logger.info(f"Found {len(self.tif_files)} relevant TIF files for class selection {self.class_selection}.")

        combined_df = self.process_files(self.tif_files, OUTPUT_PATH)
        self.save_results(combined_df)

    def filter_tif_files_by_selection(self):
        """
        Filters the TIF files to match the selected class based on class_selection.
        :return: List of filtered TIF files relevant to the selected class.
        """
        data_path = PREPROCESSED_DATA_PATH
        if self.class_selection == 6:
            pattern = os.path.join(data_path, 'biomes_iucn.hcl*.zip')
        elif self.class_selection == 20:
            pattern = os.path.join(data_path, 'biomes_biome6k.hcl*.zip')
        else:
            raise ValueError("Invalid class selection. Must be 6 or 20.")

        all_tif_files = glob.glob(pattern)
        self.logger.debug(f"Total TIF files found: {len(all_tif_files)}")

        if self.class_selection == 6:
            return [file for file in all_tif_files if 'iucn' in file.lower()]
        elif self.class_selection == 20:
            return [file for file in all_tif_files if 'biome6k' in file.lower()]
        return []

    def plot_tif(self, tif_file: str, output_path: str):
        """
        Transforms a TIFF file into a PNG format and saves it to the specified output path.
        :param tif_file: Reads a TIFF file based on the number of vegetation classes (either 6 or 20).
        :param output_path: String of the output folder.
        """
        if self.class_selection == 20:
            colors = colors_20
            labels = labels_20
        elif self.class_selection == 6:
            colors = colors_6
            labels = labels_6
        else:
            raise ValueError("Invalid number of classes. Must be 6 or 20.")

        cmap = mcolors.ListedColormap(colors)

        folder_name = os.path.normpath(tif_file)
        folder_name = folder_name.split(os.sep)[-1]

        tif_file = f"zip+file://{tif_file}!{folder_name[:-3]}tif"

        with rasterio.open(tif_file) as src:
            img = src.read(1)
            unique_values = np.unique(img)

            if len(unique_values) > len(colors):
                raise ValueError(f"The image has more than {len(colors)} classes.")

            plt.figure(figsize=(14, 10))
            plt.imshow(img, cmap=cmap, interpolation='nearest')
            cbar = plt.colorbar(ticks=range(len(colors)))
            cbar.ax.set_yticklabels(labels)
            cbar.ax.yaxis.set_tick_params(labelsize=10)
            cbar.ax.yaxis.set_ticks_position('right')

            filename = os.path.splitext(os.path.basename(tif_file))[0]
            plt.title(filename)
            plt.tight_layout(rect=[0, 0, 0.85, 1])
            plt.savefig(output_path)
            plt.close()

    def calculate_area(self, tif_file: str):
        """
        The complete global area represented in the TIFF file is calculated.
        :param tif_file: Reads a TIFF file based on the number of vegetation classes (either 6 or 20).
        returns: Total area in km².
        """
        folder_name = os.path.normpath(tif_file)
        folder_name = folder_name.split(os.sep)[-1]
        tif_file = f"zip+file://{tif_file}!{folder_name[:-3]}tif"

        with rasterio.open(tif_file) as src:
            resolution = src.res[0]
            width = src.width
            height = src.height
            total_area_km2 = width * height
            self.logger.info(f"Total area (km^2): {total_area_km2}")
            return total_area_km2

    def count_pixels_in_tif(self, tif_file: str):
        """
        Calculates the number of pixel in the TIFF file for each category of vegetation area and provides the
        corresponding percentage distribution.
        :param tif_file: Reads a TIFF file based on the number of vegetation classes (either 6 or 20).
        returns: Dataframe with km² for different classes.
        """
        if self.class_selection == 20:
            colors = colors_20
            labels = labels_20
        elif self.class_selection == 6:
            colors = colors_6
            labels = labels_6
        else:
            raise ValueError("Invalid class selection. Must be 6 or 20.")

        folder_name = os.path.normpath(tif_file)
        folder_name = folder_name.split(os.sep)[-1]
        tif_file = f"zip+file://{tif_file}!{folder_name[:-3]}tif"

        with rasterio.open(tif_file) as src:
            img = src.read(1)
            results_df = pd.DataFrame(columns=['value', 'class name', 'pixel count', 'percentage (include 0)',
                                               'percentage (exclude 0)'])
            total_pixels = np.prod(img.shape)

            for value in range(len(colors)):
                pixel_count = np.count_nonzero(img == value)
                percentage_include_0 = (pixel_count / total_pixels) * 100

                if value == 0:
                    percentage_exclude_0 = 0
                else:
                    percentage_exclude_0 = (pixel_count / np.count_nonzero(img != 0)) * 100

                results_df = pd.concat([results_df, pd.DataFrame({
                    'Value': [value],
                    'Class Name': [labels[value]],
                    'Pixel Count': [pixel_count],
                    'percentage (include 0)': [percentage_include_0],
                    'percentage (exclude 0)': [percentage_exclude_0]
                })], ignore_index=True)

            return results_df

    def get_pixel_values_by_country(self, raster_file: pd.DataFrame, log_enabled=False):
        """
        Calculates the pixels of the TIFF files for each category of vegetation area and each country on a global
        level.
        :params rater_file: Dataframe naturalearth_lowres from the geopandas package.
        returns: Dataframe with km² for every country.
        """
        num_classes = self.class_selection
        if num_classes == 20:
            labels = labels_20
        elif num_classes == 6:
            labels = labels_6
        else:
            raise ValueError("Invalid number of classes. Must be 6 or 20.")

        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        world = world.to_crs("EPSG:8857")
        world['geometry'] = world['geometry'].simplify(tolerance=0.1)
        pixel_counts_df = pd.DataFrame(columns=['country', 'ISO'] + labels + ['Total Pixels', 'Total Area (km^2)'])

        folder_name = os.path.normpath(raster_file)
        folder_name = folder_name.split(os.sep)[-1]
        raster_file = f"zip+file://{raster_file}!{folder_name[:-3]}tif"

        with rasterio.open(raster_file) as src:
            img = src.read(1)
            transform = src.transform
            total_pixels = img.size

            if log_enabled and self.logger:
                self.logger.info(f"Total pixels: {total_pixels}")

            for index, country in world.iterrows():
                geometry = [mapping(country['geometry'])]
                iso_code = country['iso_a3']

                if log_enabled and self.logger:
                    self.logger.info(f"Processing country: {country['name']} (ISO code: {iso_code})")

                try:
                    out_image, out_transform = mask(src, geometry, crop=True, nodata=0)
                    masked_img = out_image[0]
                    if masked_img.size == 0:
                        if log_enabled and self.logger:
                            self.logger.info(f"Country {country['name']} has no intersecting pixels.")
                        continue

                    masked_img = np.ma.masked_equal(masked_img, 0)

                    unique, counts = np.unique(masked_img.compressed(), return_counts=True)
                    pixel_count_dict = dict(zip(unique, counts))

                    if log_enabled and self.logger:
                        self.logger.info(f"Country: {country['name']}, class: {pixel_count_dict}")

                    row_data = {'country': country['name'], 'ISO': iso_code}
                    total_area = 0
                    for i, label in enumerate(labels):
                        pixel_count = pixel_count_dict.get(i, 0)
                        area = pixel_count
                        row_data[label] = area
                        total_area += area

                    row_data['Total Pixels'] = masked_img.compressed().size
                    row_data['Total Area (km^2)'] = total_area
                    pixel_counts_df = pd.concat([pixel_counts_df, pd.DataFrame([row_data])], ignore_index=True)
                except Exception as e:
                    self.logger.error(f"Processing {country['name']} (ISO: {iso_code}): {e}")
                    continue

        return pixel_counts_df

    def process_files(self, tif_files: str, output_dir: str):
        """
        The function gathers all processing and calculation steps.
        :param tif_files: Reads a TIFF file based on the number of vegetation classes (either 6 or 20).
        :param output_dir: Output directory path.
        :return: Dataframe with km² values for every category and country.
        """
        combined_df = pd.DataFrame()

        for tif_file_path in tqdm(tif_files, desc="Processing TIFF files"):
            original_name = os.path.splitext(os.path.basename(tif_file_path))[0]
            sheet_name = self.reduce_filename(original_name)

            self.logger.info(f"Processing {tif_file_path} with sheet name {sheet_name}")

            plot_path = os.path.join(output_dir, f"{sheet_name}.png")
            self.plot_tif(tif_file_path, plot_path)

            area = self.calculate_area(tif_file_path)
            self.logger.info(f"Calculated area for {tif_file_path}: {area} km^2")

            pixel_count_df = self.count_pixels_in_tif(tif_file_path)
            self.logger.info(f"Pixel counts calculated for {tif_file_path}")

            pixel_values_df = self.get_pixel_values_by_country(tif_file_path)
            pixel_values_df['Sheet Name'] = sheet_name

            combined_df = pd.concat([combined_df, pixel_values_df], ignore_index=True)
        return combined_df

    def reduce_filename(self, filename, length=31):
        """
        Reduces the filename to ensure it fits within the Excel sheet name limit.
        :param filename: Name of every sheet in Excel output file.
        :param length: Length of sheet name. Number of letters.
        """
        parts = filename.split('_')
        if len(parts) > 5:
            reduced = '_'.join(parts[1:6])
        else:
            reduced = filename[:length]
        return reduced[:length]

    def save_results(self, combined_df: pd.DataFrame):
        """
        Saves the country-specific data of different classes in .xlsx and .pkl.
        :param combined_df: Contains all the information about the classes for every country.
        """

        class_selection = self.class_selection
        with pd.ExcelWriter(
                os.path.join(OUTPUT_PATH, f'{self.time_stamp}_{class_selection}_class_different_sheets.xlsx'),
                engine='xlsxwriter') as writer:
            for sheet_name in combined_df['Sheet Name'].unique():
                df_sheet = combined_df[combined_df['Sheet Name'] == sheet_name]
                df_sheet.to_excel(writer, sheet_name=sheet_name[:31], index=False)

        with pd.ExcelWriter(
                os.path.join(OUTPUT_PATH, f'{self.time_stamp}_{class_selection}_class_combined.xlsx'),
                engine='xlsxwriter') as writer:
            combined_df.to_excel(writer, sheet_name='Results', index=False)

        combined_df.to_pickle(os.path.join(OUTPUT_PATH, f'{self.time_stamp}_{class_selection}_class_combined.pkl'))

        self.logger.info(f"Results saved to Excel and pickle files in {OUTPUT_PATH}")


