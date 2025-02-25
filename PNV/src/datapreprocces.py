import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import os
import zipfile
from tqdm import tqdm
import numpy as np

from PNV.user_input.default_parameters import USER_INPUT
from PNV.src.defines import PotentialNaturalVegetationArea, HildaLandUseClasses


def epsg_reproject(input_tif: str, output_tif: str, src_crs: str, dst_crs: str):
    """
    Uses rasterio to re-project tif files from one coordinate system to another.
    :param input_tif: Original tif file.
    :param output_tif: Re-projected tif file.
    :param src_crs: Source coordinate system (e.g., 4326).
    :param dst_crs: Destination reference coordinate system (e.g., 8857).
    """
    with rasterio.open(input_tif) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with rasterio.open(output_tif, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src_crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)


def zip_epsg_reproject(output_tif: str):
    """
    Transforms reprojected tif files into zip files. Deletes tif files after transformation.
    :param output_tif: Reprojected tif files.
    """

    if not os.path.exists(output_tif):
        print(f"File {output_tif} does not exist, skipping zipping.")
        return

    output_tif = output_tif[:-4]
    output_zip = output_tif.split('\\')[-1]
    zipfile.ZipFile(
        f'{output_tif}.zip', 'w', zipfile.ZIP_DEFLATED).write(f'{output_tif}.tif',
                                                              arcname=f'{output_zip}.tif')

    try:
        os.remove(f"{output_tif}.tif")
    except PermissionError:
        pass


def process_all_files(input_dir: str, output_dir: str, src_crs: str, dst_crs: str):
    """
    Copies saved tif files in the preprocessed directory. Skips tif files when the name is already available in the
    preprocessed directory.
    :param input_dir: Origin directory of tif files.
    :param output_dir: Destination directory of tif files.
    :param src_crs: Source coordinate system (e.g., 4326).
    :param dst_crs: Destination reference coordinate system (e.g., 8857).
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} does not exist.")
        return

    all_files = [
        filename for filename in os.listdir(input_dir)
        if filename.lower().endswith(".tif") and os.path.isfile(os.path.join(input_dir, filename))
    ]
    print(f"Total .tif files to process: {len(all_files)}")

    for filename in tqdm(all_files, desc="Processing .tif raw files"):
        input_path = os.path.join(input_dir, filename)
        output_filename = filename.replace('4326', '8857')
        output_path = os.path.join(output_dir, output_filename)

        if os.path.exists(output_path):
            print(f"File {output_path} already exists, skipping.")
            continue

        epsg_reproject(input_path, output_path, src_crs, dst_crs)

        if USER_INPUT['ZIPPED_DATA']:
            zip_epsg_reproject(output_path)


def reproject_raster(src_raster, target_transform, target_crs, target_shape):
    """
    Reprojects the raster to match target transform, CRS, and shape
    :param src_raster: Raster to be reprojected.
    :param target_transform: Target transform.
    :param target_crs: Target CRS.
    :param target_shape: Target shape.
    :return: Reprojected raster as numpy array.
    """
    reprojected_data = np.empty(target_shape, dtype=np.float32)

    reproject(
        source=src_raster.read(1),
        destination=reprojected_data,
        src_transform=src_raster.transform,
        src_crs=src_raster.crs,
        dst_transform=target_transform,
        dst_crs=target_crs,
        resampling=Resampling.nearest
    )

    return reprojected_data


def read_raster(file_path: str):
    """
    Reads in raster dataset
    :param file_path: Path to raster file to be read.
    :return: Raster dataset.
    """
    with rasterio.open(file_path) as dataset:
        data = dataset.read(1)
        transform = dataset.transform
        crs = dataset.crs
        bounds = dataset.bounds
        meta = dataset.meta
    return dataset, data, transform, crs, bounds, meta


def reproject_and_save(src_raster_path, output_path, forest_raster_path, zipped_data, logger):
    """
    Reprojects the source raster to the target transform and CRS, then saves it to a specified folder.
    :param src_raster_path: Path to the source raster file.
    :param output_path: Folder to save the reprojected raster.
    :param forest_raster_path: Path to the forest raster file.
    :param zipped_data: Flag to control if zipped forest data is used.
    :param logger: Logger instance.
    """
    if zipped_data:
        folder_name = forest_raster_path.split(os.sep)[-1]
        forest_raster_path = f"zip+file://{forest_raster_path}!{folder_name[:-3]}tif"

    forest_data_rast, forest_data_np, target_transform, target_crs, bounds1, meta1 = read_raster(forest_raster_path)
    target_shape = forest_data_np.shape

    with rasterio.open(src_raster_path) as src_raster:

        if target_crs != src_raster.crs:
            logger.info(f'The CRS of the agriculture and forest rasters do not match. Reprojection is needed.')

        if target_transform != src_raster.transform:
            logger.info(f'The rasters of the agriculture and forest rasters are not aligned. Resampling is required.')
            logger.info(f'Reproject and resample agriculture raster.')

            if not os.path.isfile(output_path):
                reprojected_data = np.empty(target_shape, dtype=np.float32)

                reproject(
                    source=src_raster.read(1),
                    destination=reprojected_data,
                    src_transform=src_raster.transform,
                    src_crs=src_raster.crs,
                    dst_transform=target_transform,
                    dst_crs=target_crs,
                    resampling=Resampling.nearest
                )

                output_meta = {
                    'driver': 'GTiff',
                    'count': 1,
                    'dtype': reprojected_data.dtype,
                    'crs': target_crs,
                    'transform': target_transform,
                    'width': target_shape[1],
                    'height': target_shape[0],
                }

                with rasterio.open(output_path, 'w', **output_meta) as dst_raster:
                    dst_raster.write(reprojected_data, 1)


def create_dynamic_mask(land_use_data, land_use_classes, include_exclude):
    """
    Creates a mask for a raster by checking if the values are in the specified land use classes.
    :param land_use_data: numpy array of land use data (single-band raster).
    :param land_use_classes: List of land use classes to include in the mask.
    :param include_exclude: Flag controls to include or exclude specific land use classes.
    :return: Masked numpy array with 1 for pixels matching the land use classes and 0 otherwise.
    """
    mask = np.zeros_like(land_use_data, dtype=np.uint8)

    for land_use_class in land_use_classes:
        if 'include' in include_exclude:  # To include the land use class
            mask |= (land_use_data == land_use_class)
        if 'exclude' in include_exclude:  # To exclude the land use class
            mask |= (land_use_data != land_use_class)

    return mask


def merge_with_windowing(forest_raster_path, agri_raster_path, merged_raster_path, zipped_data, selected_pnv_classes,
                         chunk_size=512):
    """
    Merges PNV raster data with land use raster data HILDA using windowing to reduce computational load.
    :param forest_raster_path: Path to the forest raster file.
    :param agri_raster_path: Path to the agriculture raster file.
    :param merged_raster_path: Path to the merged raster file.
    :param zipped_data: Flag to control if zipped forest data is used.
    :param selected_pnv_classes: Number of selected pnv classes.
    :param chunk_size: Chunk size in bytes.
    """
    with rasterio.open(forest_raster_path) as forest_raster:
        forest_transform = forest_raster.transform
        forest_crs = forest_raster.crs
        forest_width = forest_raster.width
        forest_height = forest_raster.height

        with rasterio.open(agri_raster_path) as agri_raster:

            with rasterio.open(merged_raster_path, 'w', driver='GTiff', count=1, dtype=np.float32,
                               crs=forest_crs, transform=forest_transform, width=forest_width,
                               height=forest_height) as output_raster:

                # Iterate over the raster in windows
                for i in range(0, forest_height, chunk_size):
                    for j in range(0, forest_width, chunk_size):
                        # Ensure that the window does not exceed the raster bounds
                        chunk_height = min(chunk_size, forest_raster.shape[0] - i)
                        chunk_width = min(chunk_size, forest_raster.shape[1] - j)

                        # Define the window to read from both rasters
                        window = rasterio.windows.Window(j, i, chunk_width, chunk_height)

                        # Read the corresponding slice from both rasters
                        forest_chunk = forest_raster.read(1, window=window)
                        agri_chunk = agri_raster.read(1, window=window)

                        if selected_pnv_classes == 6:
                            filter_forest_class = PotentialNaturalVegetationArea.forest_classes_6.value
                            filter_forest_class = list(filter_forest_class.keys())
                        if selected_pnv_classes == 20:
                            filter_forest_class = PotentialNaturalVegetationArea.forest_classes_20.value
                            filter_forest_class = list(filter_forest_class.keys())

                        forest_mask = create_dynamic_mask(land_use_data=forest_chunk,
                                                          land_use_classes=filter_forest_class,
                                                          include_exclude='include')
                        # Create a mask for agricultural and urban areas from HILDA+
                        filter_other_land_use_class = HildaLandUseClasses.other_lu_classes.value
                        filter_other_land_use_class = list(filter_other_land_use_class.keys())

                        other_land_use_mask = create_dynamic_mask(land_use_data=agri_chunk,
                                                                  land_use_classes=filter_other_land_use_class,
                                                                  include_exclude='exclude')

                        forest_not_in_agriculture_and_urban = forest_mask & other_land_use_mask

                        remaining_forest_area = np.where(forest_not_in_agriculture_and_urban, forest_chunk, np.nan)

                        output_raster.write(remaining_forest_area, 1, window=window)

    if zipped_data:
        zip_epsg_reproject(merged_raster_path)

