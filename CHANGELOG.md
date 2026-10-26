# Changelog

## [v2.0.0] - 2025-04-08
### New Features
- **Merge PFA data with other land use types:**
  - Spatial data from Bonannella et al. (2023) are merged with urban and agricultural land use data from HILDA+ (Winkler et al., 2021).
  - Windowing and downscaling approaches are used to reduce computational load.
- **Toolbox:**
  - Extended toolbox to process merged forest, agricultural, and urban land use data.
- **OS compatibility:**
  - Reworked path handling for zipped raster data using GDAL VSI paths (/vszip//) and consistent extraction of internal .tif paths via zipfile to ensure compatibility 
across Windows, Linux, Ubuntu, and macOS.

## [v1.0.0] - 2025-02-27
### Initial Release
- **Process PNV data from Bonannella et al. (2023):**
  - Processed and aggregated PNV data from Bonannella et al. (2023) to country-specific PFA data.
  - Support for 6 and 20 PNV classes.

 - **Toolbox:**
  - Built-in solution for rapid and interactive exploration of aggregated PFA data.
  - Built-in validation step for aggregated data.