import os

from .base import LCIA, data_dir, fiona, geocollections, regionalized

"""When is water not water? When it is in water!

We are assessing freshwater consumption, and so some water flows are excluded."""

SURFACE_WATER = [
    ("Fresh water (obsolete)", ("water", "surface water"), -1),
    ("Water", ("water",), -1),
    ("Water", ("water", "surface water"), -1),
    ("Water, cooling, unspecified natural origin", ("natural resource", "in water"), 1),
    ("Water, lake", ("natural resource", "in water"), 1),
    ("Water, river", ("natural resource", "in water"), 1),
    (
        "Water, turbine use, unspecified natural origin",
        ("natural resource", "in water"),
        1,
    ),
    ("Water, unspecified natural origin", ("natural resource", "in water"), 1),
]

GROUND_WATER = [
    ("Water", ("water", "ground-"), -1),
    # ('Water', ('water', 'ground-, long-term')),
    ("Water, unspecified natural origin", ("natural resource", "in ground"), 1),
    ("Water, well, in ground", ("natural resource", "in water"), 1),
]


class Water(LCIA):
    def _water_flows(self, kind="all"):
        mapping = {
            "all": SURFACE_WATER + GROUND_WATER,
            "surface": SURFACE_WATER,
            "ground": GROUND_WATER,
        }
        flows = mapping[kind]

        for act in self.db:
            name, categories = act["name"], tuple(act["categories"])
            for x, y, sign in flows:
                if name == x and categories == y:
                    yield act.key, sign


class WaterHumanHealthMarginal(Water):
    vector_ds = os.path.join(data_dir, "water_hh.gpkg")
    geocollection = "watersheds-hh"
    column = "HH"

    name = ("LC-IMPACT", "Water Use", "Human Health", "Marginal")
    global_cf = 1.8e-7
    unit = "DALY/m3"
    description = """The impact assessment method for assessing water consumption concerning the area of protection of human health is described based on Pfister et al. (2009) for the impact pathway (marginal CF), Pfister and Hellweg (2011) for uncertainty assessment, and Pfister and Bayer (2013) for average CFs.

    Only the 'certain' level of uncertainty is provided."""
    url = "http://lc-impact.eu/human-health-water-stress"

    @regionalized
    def setup_geocollections(self):
        if self.geocollection not in geocollections:
            geocollections[self.geocollection] = {
                "filepath": self.vector_ds,
                "field": "BAS34S_ID",
            }

    def global_cfs(self):
        for key, sign in self._water_flows():
            yield ((key, self.global_cf * sign, "GLO"))

    @regionalized
    def regional_cfs(self):
        water_flows = list(self._water_flows())

        for obj in self.global_cfs():
            yield obj

        with fiona.Env():
            with fiona.open(self.vector_ds) as src:
                for feat in src:
                    for key, sign in water_flows:
                        yield (
                            key,
                            feat["properties"][self.column]
                            * 1e-9
                            * sign,  # Convert km3 to m3
                            (self.geocollection, feat["properties"]["BAS34S_ID"]),
                        )


class WaterHumanHealthAverage(WaterHumanHealthMarginal):
    name = ("LC-IMPACT", "Water Use", "Human Health", "Average")
    global_cf = 1.3e-7
    column = "HH_AVG"


class WaterEcosystemQualityCertain(Water):
    vector_ds = os.path.join(data_dir, "water_eq_sw_core.gpkg")
    geocollection = "watersheds-eq-sw-certain"
    column = "val"

    name = (
        "LC-IMPACT",
        "Water Use",
        "Ecosystem Quality",
        "Surface Water",
        "Marginal",
        "Certain",
    )
    global_cf = 1.63e-13
    unit = "PDF·yr/m3"
    description = """The description of the impact assessment approach for quantifying impacts from water consumption on biodiversity is based on Verones et al. (submitted), which is a continuation from Verones et al. (2013a) and Verones et al. (2013b), as well as Chaudhary et al. (2015)."""
    url = "http://lc-impact.eu/ecosystem-quality-water-stress"

    _flows_label = "surface"

    @regionalized
    def setup_geocollections(self):
        if self.geocollection not in geocollections:
            geocollections[self.geocollection] = {
                "filepath": self.vector_ds,
                "field": "id",
            }

    def global_cfs(self):
        for key, sign in self._water_flows(self._flows_label):
            yield ((key, self.global_cf * sign, "GLO"))

    @regionalized
    def regional_cfs(self):
        water_flows = list(self._water_flows(self._flows_label))

        for obj in self.global_cfs():
            yield obj

        with fiona.Env():
            with fiona.open(self.vector_ds) as src:
                for feat in src:
                    for key, sign in water_flows:
                        yield (
                            key,
                            feat["properties"][self.column] * sign,
                            (self.geocollection, feat["properties"]["id"]),
                        )


class WaterEcosystemQualityAll(WaterEcosystemQualityCertain):
    vector_ds = os.path.join(data_dir, "water_eq_sw_extended.gpkg")
    geocollection = "watersheds-eq-sw-all"

    name = (
        "LC-IMPACT",
        "Water Use",
        "Ecosystem Quality",
        "Surface Water",
        "Marginal",
        "All",
    )
    global_cf = 1.65e-13

    _flows_label = "all"
