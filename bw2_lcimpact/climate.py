import os

import xlrd

from .base import LCIA, data_dir

CATEGORIES = {
    ("air",),
    ("air", "non-urban air or from high stacks"),
    ("air", "lower stratosphere + upper troposphere"),
    ("air", "low population density, long-term"),
    ("air", "urban air close to ground"),
}


def _get_column(ws, index):
    return [
        (ws.cell(row, 0).value, ws.cell(row, index).value) for row in range(1, ws.nrows)
    ]


def get_values_by_column(column):
    wb = xlrd.open_workbook(os.path.join(data_dir, "climate-change.xlsx"))
    mapping_data = _get_column(wb.sheet_by_name("mapping"), 1)
    mapping = {x: [] for x, y in mapping_data}
    for x, y in mapping_data:
        mapping[x].append(y)

    cf_data = _get_column(wb.sheet_by_name("cfs"), column)
    for name, value in cf_data:
        for mapped_name in mapping.get(name, []):
            yield (mapped_name, value)


class ClimateChange(LCIA):
    geocollection = None

    def setup_geocollections(self):
        return

    def regional_cfs(self):
        raise NotImplementedError

    def global_cfs(self):
        cfs = {x: y for x, y in get_values_by_column(self.column)}

        for flow in self.db:
            if flow["name"] in cfs and tuple(flow["categories"]) in CATEGORIES:
                yield ((flow.key, cfs[flow["name"]], "GLO"))


class ClimateChangeHumanHealth(ClimateChange):
    unit = "DALY/kg"
    description = """"""
    url = "http://lc-impact.eu/human-health-climate-change"


class ClimateChangeHumanHealthCertain100Years(ClimateChangeHumanHealth):
    name = (
        "LC-IMPACT",
        "Climate Change",
        "Human Health",
        "Marginal",
        "Certain",
        "100 Years",
    )
    column = 1


class ClimateChangeHumanHealthAll100Years(ClimateChangeHumanHealth):
    name = (
        "LC-IMPACT",
        "Climate Change",
        "Human Health",
        "Marginal",
        "All",
        "100 Years",
    )
    column = 2


class ClimateChangeHumanHealthCertainInfinite(ClimateChangeHumanHealth):
    name = (
        "LC-IMPACT",
        "Climate Change",
        "Human Health",
        "Marginal",
        "Certain",
        "Infinite",
    )
    column = 3


class ClimateChangeHumanHealthAllInfinite(ClimateChangeHumanHealth):
    name = (
        "LC-IMPACT",
        "Climate Change",
        "Human Health",
        "Marginal",
        "All",
        "Infinite",
    )
    column = 4


class ClimateChangeTerrestrialEcosystems(ClimateChange):
    unit = "PDF year/kg"
    description = """"""
    url = "http://lc-impact.eu/ecosystem-quality-climate-change"


class ClimateChangeTerrestrialEcosystemsCertain100Years(
    ClimateChangeTerrestrialEcosystems
):
    name = (
        "LC-IMPACT",
        "Climate Change",
        "Terrestrial Ecosystems",
        "Marginal",
        "Certain",
        "100 Years",
    )
    column = 5


class ClimateChangeTerrestrialEcosystemsAll100Years(ClimateChangeTerrestrialEcosystems):
    name = (
        "LC-IMPACT",
        "Climate Change",
        "Terrestrial Ecosystems",
        "Marginal",
        "All",
        "100 Years",
    )
    column = 6


class ClimateChangeTerrestrialEcosystemsCertainInfinite(
    ClimateChangeTerrestrialEcosystems
):
    name = (
        "LC-IMPACT",
        "Climate Change",
        "Terrestrial Ecosystems",
        "Marginal",
        "Certain",
        "Infinite",
    )
    column = 7


class ClimateChangeTerrestrialEcosystemsAllInfinite(ClimateChangeTerrestrialEcosystems):
    name = (
        "LC-IMPACT",
        "Climate Change",
        "Terrestrial Ecosystems",
        "Marginal",
        "All",
        "Infinite",
    )
    column = 8


class ClimateChangeAquaticEcosystems(ClimateChangeTerrestrialEcosystems):
    description = """"""


class ClimateChangeAquaticEcosystemsAll100Years(ClimateChangeAquaticEcosystems):
    name = (
        "LC-IMPACT",
        "Climate Change",
        "Aquatic Ecosystems",
        "Marginal",
        "All",
        "100 Years",
    )
    column = 10


class ClimateChangeAquaticEcosystemsAllInfinite(ClimateChangeAquaticEcosystems):
    name = (
        "LC-IMPACT",
        "Climate Change",
        "Aquatic Ecosystems",
        "Marginal",
        "All",
        "Infinite",
    )
    column = 12
