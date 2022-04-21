import os

from .base import LCIA, data_dir, fiona, geocollections, regionalized

GLOBAL_CFS = {
    "Particulates, < 2.5 um": 6.29e-4,
    "Ammonia": 1.6e-4,
    "Nitrogen oxides": 7.62e-5,
    "Sulfur dioxide": 1.83e-4,
}
ECOINVENT_TO_VECTOR = {
    "Particulates, < 2.5 um": "PM25",
    "Nitrogen oxides": "Nox",
    "Sulfur dioxide": "SO2",
    "Ammonia": "NH3",
}
CATEGORIES = {
    ("air",),
    ("air", "non-urban air or from high stacks"),
    ("air", "lower stratosphere + upper troposphere"),
    ("air", "low population density, long-term"),
    ("air", "urban air close to ground"),
}


class ParticulateMatterFormationCertain(LCIA):
    vector_ds = os.path.join(data_dir, "particulate_matter.gpkg")
    geocollection = "particulate-matter"

    name = ("LC-IMPACT", "Particulate Matter Formation", "Marginal", "Certain")
    unit = "DALY/kg"
    description = """The impact assessment method for assessing damage to human health due to primary PM2.5 is described based on Van Zelm et al. (2016).

    Only actual PM emissions are considered in the 'certain' level."""
    url = "http://lc-impact.eu/human-health-particular-matter-formation"

    @regionalized
    def setup_geocollections(self):
        if self.geocollection not in geocollections:
            geocollections[self.geocollection] = {
                "filepath": self.vector_ds,
                "field": "TM5",
            }

    def global_cfs(self):
        for flow in self.db:
            if (
                flow["name"] == "Particulates, < 2.5 um"
                and flow["categories"] in CATEGORIES
            ):
                yield ((flow.key, GLOBAL_CFS[flow["name"]], "GLO"))

    @regionalized
    def regional_cfs(self):
        flows = {"Particulates, < 2.5 um": []}
        for flow in self.db:
            if (
                flow["name"] == "Particulates, < 2.5 um"
                and flow["categories"] in CATEGORIES
            ):
                flows[flow["name"]].append(flow.key)

        for obj in self.global_cfs():
            yield obj

        with fiona.Env():
            with fiona.open(self.vector_ds) as src:
                for feat in src:
                    for flow, keys in flows.items():
                        for key in keys:
                            yield (
                                key,
                                feat["properties"][ECOINVENT_TO_VECTOR[flow]],
                                (self.geocollection, feat["properties"]["TM5"]),
                            )


class ParticulateMatterFormationAll(LCIA):
    vector_ds = os.path.join(data_dir, "particulate_matter.gpkg")
    geocollection = "particulate-matter"

    name = ("LC-IMPACT", "Particulate Matter Formation", "Marginal", "All")
    unit = "DALY/kg"
    description = """The impact assessment method for assessing damage to human health due to primary PM2.5 and PM2.5 precursor emissions is described based on Van Zelm et al. (2016)."""
    url = "http://lc-impact.eu/human-health-particular-matter-formation"

    @regionalized
    def setup_geocollections(self):
        if self.geocollection not in geocollections:
            geocollections[self.geocollection] = {
                "filepath": self.vector_ds,
                "field": "TM5",
            }

    def global_cfs(self):
        for flow in self.db:
            if flow["name"] in GLOBAL_CFS and flow["categories"] in CATEGORIES:
                yield ((flow.key, GLOBAL_CFS[flow["name"]], "GLO"))

    @regionalized
    def regional_cfs(self):
        flows = {k: [] for k in GLOBAL_CFS}
        for flow in self.db:
            if flow["name"] in GLOBAL_CFS and flow["categories"] in CATEGORIES:
                flows[flow["name"]].append(flow.key)

        for obj in self.global_cfs():
            yield obj

        with fiona.Env():
            with fiona.open(self.vector_ds) as src:
                for feat in src:
                    for flow, keys in flows.items():
                        for key in keys:
                            yield (
                                key,
                                feat["properties"][ECOINVENT_TO_VECTOR[flow]],
                                (self.geocollection, feat["properties"]["TM5"]),
                            )
