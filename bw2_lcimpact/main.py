from .pm import ParticulateMatterFormation
from .water import (
    WaterHumanHealthMarginal,
    WaterHumanHealthAverage,
    WaterEcosystemQualityCore,
    WaterEcosystemQualityExtended,
)

METHODS = (
    ParticulateMatterFormation,
    WaterHumanHealthMarginal,
    WaterHumanHealthAverage,
    WaterEcosystemQualityCore,
    WaterEcosystemQualityExtended,
)

def import_global_lcimpact(biosphere='biosphere3'):
    pass

def import_regionalized_lcimpact(biosphere='biosphere3'):
    pass
