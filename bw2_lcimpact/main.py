from .pm import ParticulateMatterFormationAll, ParticulateMatterFormationCertain
from .water import (
    WaterHumanHealthMarginal,
    WaterHumanHealthAverage,
    WaterEcosystemQualityCertain,
    WaterEcosystemQualityAll,
)
from .climate import (
    ClimateChangeHumanHealthCertain100Years,
    ClimateChangeHumanHealthAll100Years,
    ClimateChangeHumanHealthCertainInfinite,
    ClimateChangeHumanHealthAllInfinite,
    ClimateChangeTerrestrialEcosystemsCertain100Years,
    ClimateChangeTerrestrialEcosystemsAll100Years,
    ClimateChangeTerrestrialEcosystemsCertainInfinite,
    ClimateChangeTerrestrialEcosystemsAllInfinite,
    ClimateChangeAquaticEcosystemsAll100Years,
    ClimateChangeAquaticEcosystemsAllInfinite,
)
from .land_use import (
    LandUseOccupationMarginal,
    LandUseOccupationAverage,
    LandUseTransformationMarginalCertain,
    LandUseTransformationMarginalAll,
    LandUseTransformationAverageCertain,
    LandUseTransformationAverageAll,
)
from .base import remote, regionalized

METHODS = (
    LandUseOccupationMarginal,
    LandUseOccupationAverage,
    LandUseTransformationMarginalCertain,
    LandUseTransformationMarginalAll,
    LandUseTransformationAverageCertain,
    LandUseTransformationAverageAll,
    ParticulateMatterFormationAll,
    ParticulateMatterFormationCertain,
    WaterHumanHealthAverage,
    WaterHumanHealthMarginal,
    WaterEcosystemQualityCertain,
    WaterEcosystemQualityAll,
)


def import_global_lcimpact(biosphere="biosphere3"):
    for method in METHODS:
        method(biosphere).import_global_method()


@regionalized
def import_regionalized_lcimpact(biosphere="biosphere3"):
    for method in METHODS:
        try:
            method(biosphere).import_regional_method()
        except NotImplemented:
            pass

    try:
        remote.intersection("world", "watersheds-hh")
        remote.intersection("world", "watersheds-eq-sw-certain")
        remote.intersection("world", "watersheds-eq-sw-all")
        remote.intersection("world", "particulate-matter")
        remote.intersection("world", "ecoregions")

        remote.intersection_as_new_geocollection(
            "world", "watersheds-hh", "world-topo-watersheds-hh"
        )
        remote.intersection_as_new_geocollection(
            "world", "watersheds-eq-sw-certain", "world-topo-watersheds-eq-sw-certain"
        )
        remote.intersection_as_new_geocollection(
            "world", "watersheds-eq-sw-all", "world-topo-watersheds-eq-sw-all"
        )
        remote.intersection_as_new_geocollection(
            "world", "particulate-matter", "world-topo-particulate-matter"
        )
        remote.intersection_as_new_geocollection(
            "world", "ecoregions", "world-topo-ecoregions"
        )
    except:
        print("Can't import data from pandarus remote")
