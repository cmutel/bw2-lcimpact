import os

from .base import LCIA, data_dir, fiona, geocollections, regionalized

flow_mapping = {
    "annual": [
        "Occupation, annual crop",
        "Occupation, annual crop, flooded crop",
        "Occupation, annual crop, greenhouse",
        "Occupation, annual crop, irrigated",
        "Occupation, annual crop, irrigated, extensive",
        "Occupation, annual crop, irrigated, intensive",
        "Occupation, annual crop, non-irrigated",
        "Occupation, annual crop, non-irrigated, extensive",
        "Occupation, annual crop, non-irrigated, intensive",
        "Occupation, arable land, unspecified use",
        "Occupation, arable, conservation tillage (obsolete)",
        "Occupation, arable, conventional tillage (obsolete)",
        "Occupation, arable, reduced tillage (obsolete)",
        "Occupation, field margin/hedgerow",
    ],
    "permanent": [
        "Occupation, permanent crop",
        "Occupation, permanent crop, irrigated",
        "Occupation, permanent crop, irrigated, extensive",
        "Occupation, permanent crop, irrigated, intensive",
        "Occupation, permanent crop, non-irrigated",
        "Occupation, permanent crop, non-irrigated, extensive",
        "Occupation, permanent crop, non-irrigated, intensive",
    ],
    "pasture": [
        "Occupation, pasture, man made",
        "Occupation, pasture, man made, extensive",
        "Occupation, pasture, man made, intensive",
        "Occupation, grassland, natural, for livestock grazing",
        "Occupation, heterogeneous, agricultural",
    ],
    "urban": [
        "Occupation, traffic area, rail network",
        "Occupation, traffic area, rail/road embankment",
        "Occupation, traffic area, road network",
        "Occupation, construction site",
        "Occupation, industrial area",
        "Occupation, urban, continuously built",
        "Occupation, urban, discontinuously built",
        "Occupation, urban, green area",
        "Occupation, mineral extraction site",
        "Occupation, dump site",
    ],
    "extensive": ["Occupation, forest, extensive"],
    "intensive": ["Occupation, forest, intensive", "Occupation, forest, unspecified"],
}


class LandUse(LCIA):
    vector_ds = os.path.join(data_dir, "land_use.gpkg")
    geocollection = "ecoregions"
    suffix = ""

    description = """The method is based on the UNEP-SETAC guideline on global land use impact assessment on biodiversity in LCA (Koellner et al. 2013a) concerning the area of protection of ecosystem quality. The approach proposed by Chaudhary et al. 2015 using countryside species-area relationship (SAR) is used for calculating ecoregion specific marginal and average characterization factors (CFs) for biodiversity loss for both land occupation and transformation.

    Only the 'certain' level of uncertainty is provided for occupation."""
    url = "http://lc-impact.eu/ecosystem-quality-land-stress"

    @regionalized
    def setup_geocollections(self):
        if self.geocollection not in geocollections:
            geocollections[self.geocollection] = {
                "filepath": self.vector_ds,
                "field": "eco_code",
            }

    def get_flow_dictionary(self):
        all_flows = set.union(*[set(x) for x in flow_mapping.values()])
        return {act["name"]: act for act in self.db if act["name"] in all_flows}

    def global_cfs(self):
        fd = self.get_flow_dictionary()

        for key, names in flow_mapping.items():
            cf = self.global_cf_dict[key]
            for name in names:
                yield ((fd[name].key, cf, "GLO"))

    def get_column(self, label):
        return self.stem + label + self.suffix

    @regionalized
    def regional_cfs(self):
        fd = self.get_flow_dictionary()

        for obj in self.global_cfs():
            yield obj

        with fiona.Env():
            with fiona.open(self.vector_ds) as src:
                for feat in src:
                    for label, names in flow_mapping.items():
                        for name in names:
                            yield (
                                fd[name].key,
                                feat["properties"][self.get_column(label)],
                                (self.geocollection, feat["properties"]["eco_code"]),
                            )


class LandUseOccupation(LandUse):
    unit = "PDF/m2"


class LandUseOccupationMarginal(LandUseOccupation):
    name = ("LC-IMPACT", "Land Use", "Occupation", "Marginal", "Certain")
    stem = "occup_marginal_"

    global_cf_dict = {
        "annual": 6.18e-15,
        "permanent": 4.6e-15,
        "pasture": 3.81e-15,
        "urban": 6.71e-15,
        "extensive": 1.26e-15,
        "intensive": 3.4e-15,
    }


class LandUseOccupationAverage(LandUseOccupation):
    name = ("LC-IMPACT", "Land Use", "Occupation", "Average", "Certain")
    stem = "occup_average_"

    global_cf_dict = {
        "annual": 8.4e-14,
        "permanent": 6e-14,
        "pasture": 5.2e-14,
        "urban": 9.8e-14,
        "extensive": 1.5e-14,
        "intensive": 4.3e-14,
    }


class LandUseTransformation(LandUse):
    unit = "PDF·yr/m2"


class LandUseTransformationMarginalCertain(LandUseTransformation):
    name = ("LC-IMPACT", "Land Use", "Transformation", "Marginal", "Certain")
    stem = "trans_marginal_"

    global_cf_dict = {
        "annual": 4.33e-13,
        "permanent": 3.23e-13,
        "pasture": 2.71e-13,
        "urban": 4.68e-13,
        "extensive": 8.91e-14,
        "intensive": 2.41e-13,
    }


class LandUseTransformationMarginalAll(LandUseTransformation):
    name = ("LC-IMPACT", "Land Use", "Transformation", "Marginal", "All")
    stem = "trans_marginal_"
    suffix = "_100"

    global_cf_dict = {
        "annual": 7.51e-13,
        "permanent": 5.58e-13,
        "pasture": 4.51e-13,
        "urban": 8.19e-13,
        "extensive": 1.51e-13,
        "intensive": 3.75e-13,
    }


class LandUseTransformationAverageCertain(LandUseTransformation):
    name = ("LC-IMPACT", "Land Use", "Transformation", "Average", "Certain")
    stem = "trans_average_"

    global_cf_dict = {
        "annual": 6.1e-12,
        "permanent": 4.3e-12,
        "pasture": 3.6e-12,
        "urban": 6.9e-12,
        "extensive": 1.1e-12,
        "intensive": 3.1e-12,
    }


class LandUseTransformationAverageAll(LandUseTransformation):
    name = ("LC-IMPACT", "Land Use", "Transformation", "Average", "All")
    stem = "trans_average_"
    suffix = "_100"

    global_cf_dict = {
        "annual": 1e-11,
        "permanent": 7.2e-12,
        "pasture": 5.8e-12,
        "urban": 1.2e-11,
        "extensive": 1.7e-12,
        "intensive": 4.6e-12,
    }
