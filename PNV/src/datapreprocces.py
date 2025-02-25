import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import os
import zipfile
from tqdm import tqdm


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
        zip_epsg_reproject(output_path)

