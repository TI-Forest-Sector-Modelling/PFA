from enum import Enum


class PotentialNaturalVegetationArea(Enum):
    """
    Class holding information and classification about IUCN and biomes from Input data.
    """
    forest_classes_6 = {1: "Tropical-subtropical forest biome",
                        2: "Temperate-boreal forests and woodlands biome",
                        3: "Shrublands and shrubby woodland biome"}
    forest_classes_20 = {1: "Cold deciduous forest",
                         2: "Cold evergreen needleleaf forest",
                         3: "Cool evergreen needleleaf forest",
                         4: "Cool mixed forest",
                         5: "Cool temperate rainforest",
                         12: "Temperate deciduous broadleaf forest",
                         13: "Temperate evergreen needleleaf open woodland",
                         14: "Temperate sclerophyll woodland and shrubland",
                         15: "Tropical deciduous broadleaf forest and woodland",
                         16: "Tropical evergreen broadleaf forest",
                         18: "Tropical semi-evergreen broadleaf forest",
                         19: "Warm-temperate evergreen broadleaf and mixed forest",
                         20: "Xerophytic woods/scrub"}


class HildaLandUseClasses(Enum):
    other_lu_classes = {11: "urban",
                        22: "cropland",
                        33: "pasture/rangeland"}


class Coordinates(Enum):
    """
    Class holding coordinates of regions for different levels of aggregation (continents and fao_regions).
    For each region coordinates are provided as [longitudes, latitudes]. This order is important for the processing.
    """

    coord_fao_reg_default_proj = {'Central America': [0.599601, -110.533466],
                                  'East Asia': [20.311473, 112.854275],
                                  'Eastern and Southern Africa': [-17.846607, 40.598418],
                                  'Europe': [53.144170, -15.764096],
                                  'North America': [38.441589, -108.664487],
                                  'Northern Africa': [23.852071, 1.750762],
                                  'Oceania': [-31.752199, 148.681687],
                                  'Russian Federation': [53.906474, 82.063637],
                                  'South America': [-38.379514, -87.570737],
                                  'South and Southeast Asia': [-6.573701, 79.426918],
                                  'Western and Central Africa': [-20.173133, -14.245331],
                                  'Western and Central Asia': [27.182714, 37.961699]
                                  }

    coord_continents_default_proj = {'Africa': [-20.173133, -14.245331],
                                     'Asia': [-6.573701, 79.426918],
                                     'Europe': [53.144170, -15.764096],
                                     'North and Central America': [31.868599, -107.853879],
                                     'Oceania': [-31.752199, 148.681687],
                                     'Russian Federation': [53.906474, 82.063637],
                                     'South America': [-38.379514, -87.570737],
                                     }

    coord_fao_reg_winkel_proj = {'Central America': [305867.2318183222, -12853109.737950647],
                                 'East Asia': [3264671.009258552, 9433038.789108526],
                                 'Eastern and Southern Africa': [-2007197.6500327415, 3623268.562951752],
                                 'Europe': [5922883.046520845, -1168071.3611151667],
                                 'North America': [3992707.9873545333, -11190558.052417643],
                                 'Northern Africa': [2655249.6012630863, 153778.56335173835],
                                 'Oceania': [-4363107.271316182, 13152201.996043658],
                                 'Russian Federation': [6194311.927259675, 5964589.1623098105],
                                 'South America': [-3001841.0786965517, -7301140.287402313],
                                 'South and Southeast Asia': [-762688.2048813814, 7214127.909907286],
                                 'Western and Central Africa': [-2248462.36586317, -1264481.0178376422],
                                 'Western and Central Asia': [3052224.721807229, 3294666.15555467]
                                 }

    coord_continents_winkel_proj = {'Africa': [-2248462.36586317, -1264481.0178376422],
                                    'Asia': [-762688.2048813814, 7214127.909907286],
                                    'Europe': [5922883.046520845, -1168071.3611151667],
                                    'North and Central America': [3809725.923275502, -9115032.610324487],
                                    'Oceania': [-4076482.8104003575, 12453114.544713141],
                                    'Russian Federation': [6194311.927259675, 5964589.1623098105],
                                    'South America': [-4463881.45747334, -7169806.657055408]
                                    }
