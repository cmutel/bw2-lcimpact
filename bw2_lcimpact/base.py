import os

import wrapt
from bw2data import Database, Method

try:
    import fiona
    from bw2regional import geocollections, remote
except ImportError:
    fiona = None
    geocollections, remote = None, None

data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))


class GeospatialNotInstalled(Exception):
    """Geospatial libraries like fiona or bw2regional not installed"""

    pass


class NoRegionalizedSetup(Exception):
    """First run ``bw2regionalsetup` in this project"""

    pass


@wrapt.decorator
def regionalized(wrapped, instance, args, kwargs):
    if not fiona or geocollections is None:
        raise GeospatialNotInstalled
    return wrapped(*args, **kwargs)


@wrapt.decorator
def regionalized_setup(wrapped, instance, args, kwargs):
    if "world" not in geocollections:
        raise NoRegionalizedSetup
    return wrapped(*args, **kwargs)


class LCIA:
    def __init__(self, biosphere="biosphere3"):
        self.db = Database(biosphere)
        self.method = Method(self.name)

    @property
    def metadata(self):
        obj = {
            "unit": self.unit,
            "description": self.description,
            "url": self.url,
            "geocollections": [],
        }
        if self.geocollection:
            obj["geocollections"] = [self.geocollection]
        return obj

    def import_global_method(self):
        self.method.register(**self.metadata)
        self.method.write(list(self.global_cfs()))

    @regionalized
    @regionalized_setup
    def import_regional_method(self):
        self.method.register(**self.metadata)
        self.setup_geocollections()
        self.method.write(list(self.regional_cfs()))

    def __repr__(self):
        return str(self.name)
