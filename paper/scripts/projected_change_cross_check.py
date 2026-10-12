"""
cross check of projected changes of forest-related PNV against literature.
Compares the projected change in forest-related for Africa and CHina with
Yahaya et. al (2024), Sci. Rep. 14m 12315, doi:10.1038/s41598-024-61035-0 -> Africa
Luo et al, (2022), Sci. Data 9, 110, doi:10.1038/s41597-022-01204-w -> China
"""

import os
import re
import sys
import pandas as pd

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # PFA/ (scripts/ is in paper/)
sys.path.insert(0, REPO_ROOT)
from PNV.src.defines import PotentialNaturalVegetationArea

PNV_RESULTS = os.path.join(REPO_ROOT, "PNV", "data", "outputs", "6_class_combined.pkl")
GEO_DATA = os.path.join(REPO_ROOT, "PNV", "data", "raw", "geo_data.csv")
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SELECTED_PNV_CLASSES = 6

KM2_TO_MHA = 1 / 1e4  #1 Mio ha = 10,000km2

PERIOD_LABELS = {1979: "1979-2013", 2040: "2040-2060", 2061: "2061-2080"}

#reference from Yahaya et al (2024, Fig 3.a. green part)
REFERENCE_AFRICA = pd.DataFrame([
    {"source": "Yahaya et al. (2024)", "scenario": "mean of 7 SSPs", "period": "1995-2014", "area_mha": 344.0},
    {"source": "Yahaya et al. (2024)", "scenario": "mean of 7 SSPs", "period": "2041-2060", "area_mha": 278.0},
    {"source": "Yahaya et al. (2024)", "scenario": "mean of 7 SSPs", "period": "2081-2100", "area_mha": 213.0},
])

#reference from Luo et al (2022), only reports the direction of change in the text.
REFERENCE_CHINA = pd.DataFrame([
    {"source": "Luo et al. (2022)", "scenario": "SSP1-RCP2.6", "period": "2020-2100", "direction": "increase"},
    {"source": "Luo et al. (2022)", "scenario": "SSP2-RCP4.5", "period": "2020-2100", "direction": "increase"},
])

def get_forest_classes(selected_pnv_classes: int) -> list:
    """
    Returns all the names of forest-related PNV classes.
    """
    if selected_pnv_classes == 6:
        classes = PotentialNaturalVegetationArea.forest_classes_6.value
    else:
        classes = PotentialNaturalVegetationArea.forest_classes_20.value
    return list(classes.values()) if isinstance(classes, dict) else list(classes)


def parse_sheet_name(sheet_name: str) -> pd.Series:
    """
    Extracts scenario and period from the sheet name.
    """
    rcp = re.search(r"(rcp\d{2})", sheet_name)
    start_year = int(re.search(r"_a_(\d{4})", sheet_name).group(1))
    return pd.Series({"scenario": rcp.group(1) if rcp else "base", "period": PERIOD_LABELS[start_year]})


def aggregate_region(pnv_data: pd.DataFrame, selection: pd.Series, region: str) -> pd.DataFrame:
    """
    Aggregates all the forest-related PNV for a region and computes the change relative to the base period.
    """
    region_data = pnv_data[selection].groupby(["scenario", "period"])["forest_km2"].sum().reset_index()
    region_data["area_mha"] = region_data["forest_km2"] * KM2_TO_MHA
    base_area = region_data.loc[region_data["scenario"] == "base", "area_mha"].iloc[0]
    region_data["change_pct"] = (region_data["area_mha"] - base_area) / base_area * 100
    region_data.insert(0, "region", region)
    return region_data.drop(columns="forest_km2").round(1)


def main():
    pnv_data = pd.read_pickle(PNV_RESULTS)
    pnv_data["ISO"] = pnv_data["ISO"].astype(str).replace("-99", "XKX")
    geo_data = pd.read_csv(GEO_DATA)[["ISO", "continents"]]
    pnv_data = pnv_data.merge(geo_data, on="ISO", how="left")

    forest_classes = [c for c in get_forest_classes(SELECTED_PNV_CLASSES) if c in pnv_data.columns]
    pnv_data["forest_km2"] = pnv_data[forest_classes].sum(axis=1)
    pnv_data = pd.concat([pnv_data, pnv_data["Sheet Name"].apply(parse_sheet_name)], axis=1)

    results = pd.concat([
        aggregate_region(pnv_data, pnv_data["continents"] == "Africa", "Africa"),
        aggregate_region(pnv_data, pnv_data["ISO"] == "CHN", "China"),
    ], ignore_index=True)

    print(results.to_string(index=False))
    print(REFERENCE_AFRICA.to_string(index=False))
    print(REFERENCE_CHINA.to_string(index=False))

    with pd.ExcelWriter(os.path.join(OUTPUT_DIR, "projected_change_check.xlsx")) as writer:
        results.to_excel(writer, sheet_name="this_study", index=False)
        REFERENCE_AFRICA.to_excel(writer, sheet_name="ref_africa", index=False)
        REFERENCE_CHINA.to_excel(writer, sheet_name="ref_china", index=False)


if __name__ == "__main__":
    main()
