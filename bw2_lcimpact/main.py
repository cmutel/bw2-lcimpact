from .pm import (
    ParticulateMatterFormationAll,
    ParticulateMatterFormationCertain,
)
from .water import (
    WaterHumanHealthMarginal,
    WaterHumanHealthAverage,
    WaterEcosystemQualityCore,
    WaterEcosystemQualityExtended,
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
    LandUseTransformationMarginalCore,
    LandUseTransformationMarginalExtended,
    LandUseTransformationAverageCore,
    LandUseTransformationAverageExtended,
)
from .base import remote, regionalized

METHODS = (
    LandUseOccupationMarginal,
    LandUseOccupationAverage,
    LandUseTransformationMarginalCore,
    LandUseTransformationMarginalExtended,
    LandUseTransformationAverageCore,
    LandUseTransformationAverageExtended,
    ParticulateMatterFormationAll,
    ParticulateMatterFormationCertain,
    WaterHumanHealthAverage,
    WaterHumanHealthMarginal,
    WaterEcosystemQualityCore,
    WaterEcosystemQualityExtended,
)


def import_global_lcimpact(biosphere='biosphere3'):
    for method in METHODS:
        method(biosphere).import_global_method()


@regionalized
def import_regionalized_lcimpact(biosphere='biosphere3'):
    for method in METHODS:
        try:
            method(biosphere).import_regional_method()
        except NotImplemented:
            pass

    try:
        remote.intersection("world", "watersheds-hh")
        remote.intersection("world", "watersheds-eq-sw-core")
        remote.intersection("world", "watersheds-eq-sw-extended")
        remote.intersection("world", "particulate-matter")
        remote.intersection("world", "ecoregions")

        remote.intersection_as_new_geocollection(
            'world',
            'watersheds-hh',
            'world-topo-watersheds-hh'
        )
        remote.intersection_as_new_geocollection(
            'world',
            'watersheds-eq-sw-core',
            'world-topo-watersheds-eq-sw-core'
        )
        remote.intersection_as_new_geocollection(
            'world',
            'watersheds-eq-sw-extended',
            'world-topo-watersheds-eq-sw-extended'
        )
        remote.intersection_as_new_geocollection(
            'world',
            'particulate-matter',
            'world-topo-particulate-matter'
        )
        remote.intersection_as_new_geocollection(
            'world',
            'ecoregions',
            'world-topo-ecoregions'
        )
    except:
        print("Can't import data from pandarus remote")
