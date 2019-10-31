# Processing LC IMPACT outputs for import into Brightway2 and Brightway2-regional

## Water - human health

Check to make sure that the field `BAS34S_ID` is unique:

```
fp = '/Users/cmutel/Box Sync/LC-Impact (Chris Mutel)/12-water consumption/Water stress HH Spatial layers/shapefiles/LC_IMPACT_CF_.shp'
import fiona

with fiona.Env():
    with fiona.open(fp) as source:
        values = {o['properties']['BAS34S_ID'] for o in source}
        print(len(values), len(source))
```

Need to merge based on `BAS34S_ID`, and convert all to `MultiPolygon`.

Fun times: https://github.com/Toblerity/Shapely/issues/259, https://github.com/Toblerity/Shapely/issues/455

```
fp = '/Users/cmutel/Box Sync/LC-Impact (Chris Mutel)/12-water consumption/Water stress HH Spatial layers/shapefiles/LC_IMPACT_CF_.shp'
import fiona
from shapely.geometry import *
from shapely.ops import cascaded_union
from collections import defaultdict

to_mp = lambda o: MultiPolygon([o]) if isinstance(obj, Polygon) else o

cfs = defaultdict(list)

with fiona.Env():
    with fiona.open(fp) as source:
        for feat in source:
            cfs[feat['properties']['BAS34S_ID']].append(feat)

# Check to make sure CFs are consistent in watershed
keys = ('HH', 'HH_AVG', 'WSI_1', 'WSI_AVG')
for lst in cfs.values():
    for key in keys:
        assert len({o['properties'][key] for o in lst}) == 1

def better_union(geoms):
    accumulated_geom = geoms[0]
    for geom in geoms[1:]:
          accumulated_geom = cascaded_union([accumulated_geom, geom])
    if accumulated_geom.geom_type == 'Polygon':
          accumulated_geom = MultiPolygon([accumulated_geom])
    return accumulated_geom

# Union geometries
processed_cfs = []
for lst in cfs.values():
    obj = lst[0]
    obj['geometry'] = mapping(to_mp(better_union([shape(o['geometry']).buffer(0) for o in lst])))
    processed_cfs.append(obj)

with fiona.Env():
    with fiona.open(fp) as source:
        meta = source.meta
        meta['driver'] = 'GPKG'
        meta['schema']['geometry'] = 'MultiPolygon'
        with fiona.open('water_hh.gpkg', 'w', **meta) as sink:
            for f in processed_cfs:
                sink.write(f)
```

This segfaults, but write the geopackage correctly (!?)

## Water - ecosystem quality

After some investigation, the only clustering algorithm that would finish is simple k-means clustring. This is also in the notebook on k-means clustering. Same procedure for core and extended uncertainty.

```
fp = ('/Users/cmutel/Box Sync/LC-Impact (Chris Mutel)/12-water consumption/spatial layers EQ'
      '/shapefiles/CF_CORE_plants_noVS_and_animals_inclVS_noCpA_Option3_SW_PDF_perm3.tif')

import rasterio
from scipy.cluster.vq import kmeans, vq
import numpy as np
from pandarus import convert_to_vector

with rasterio.open(fp) as f:
    profile = f.profile
    array = f.read(1, masked=True)

profile.update(
    driver='GTiff',
    count=1,
    compress='lzw',
    nodata=-1,
    dtype=np.float32,
    tiled=False,
)
profile.pop('blockysize', None)
profile.pop('blockxsize', None)

array[array < 0] = -1
array = array.astype(np.float32)

raw_flat = array.data.flatten()
flat = np.log(raw_flat)
mask = np.isnan(flat)
flat = flat[~mask]

def backwards(vector):
    a = raw_flat.copy()
    a[~mask] = vector
    return a.reshape(*array.shape)

# In remaining subplots add k-means classified images
for i in range(5, 15):
    print("Calculate k-means with ", i, " cluster.")

    centroids, variance = kmeans(flat, i)
    code, distance = vq(flat, centroids)
    codeim = backwards(code)

    for value in np.unique(codeim):
        array[codeim == value] = np.median(array[codeim == value])

    with rasterio.Env():
        with rasterio.open('water_eq_core.{}.tif'.format(i), 'w', **profile) as dst:
            dst.write(array.data, 1)

for x in range(5, 15):
    print(x, convert_to_vector("water_eq_core.{}.tif".format(x)))
```

Conversion to geopackages:

```
ogr2ogr -f GPKG kmeans.8.gpkg '/Users/cmutel/Library/Application Support/pandarus/raster-conversion/748000927526f7cc4a5c8ca5ecebd81300865a4decf8631e5ff2caa8ae144ce0.1.geojson'
```

However, this produced a bunch of incorrect geometries, so clean with Shapely:

```
import fiona
from shapely.geometry import shape, mapping

with fiona.open('water_eq_sw_core.gpkg') as source:
    sink_schema = source.schema.copy()

    with fiona.open('water_eq_sw_core.fixed.gpkg', 'w', **source.profile.copy()) as sink:
        for feat in source:
            feat['geometry'] = mapping(shape(feat['geometry']).buffer(0))
            sink.write(feat)
```

## Particulate matter

Pretty simple - convert to geopackage:

```ogr2ogr -f GPKG particulate_matter.gpkg '/Users/cmutel/Box Sync/LC-Impact (Chris Mutel)/6-particulate matter formation/spatial layers/Shapefiles/CF_PM_per_Tm5FASSTregion.shp'```

All CFs in one file, file is more or less reasonable.

## Land use

Two problems - maps are way too detailed, and separate maps for all CFs even though they share a spatial scale.

Use topojson tools to simplify vector geometries. Good documentation here: https://github.com/topojson/topojson

```
sudo port install npm2
npm install topojson
```

Copy shapefiles to temp directory, and then play with various settings to get simplification right:

```
node_modules/topojson/node_modules/topojson-server/bin/geo2topo CF_Urban_Average_Occupation.geojson > topo.json
node_modules/topojson/node_modules/topojson-simplify/bin/toposimplify -F -P 0.1 topo.json > topo-s4.json
cp topo.json source5.json
node_modules/topojson/node_modules/topojson-client/bin/topo2geo -i topo-s5.json CF_Urban_Average_Occupation=source5.json
cp source5.json land_use.json
```

The polygons need to be merged into multipolygons, but there aren't different CFs for the same `eco_code`:

```
import fiona
with fiona.open("land_use.json") as f:
    print(len(f))
    print(len({o['properties']['eco_code'] for o in f}))
    print(len({(o['properties']['eco_code'], o['properties']['CF']) for o in f}))
```

Union polygons to multipolygons:

```
fp = 'land_use.json'

import fiona
from shapely.geometry import *
from shapely.ops import cascaded_union
from collections import defaultdict

to_mp = lambda o: MultiPolygon([o]) if isinstance(obj, Polygon) else o

cfs = defaultdict(list)

with fiona.Env():
    with fiona.open(fp) as source:
        meta = source.meta
        meta['driver'] = 'GeoJSON'
        meta['schema']['geometry'] = 'MultiPolygon'
        for feat in source:
            cfs[feat['properties']['eco_code']].append(feat)

def better_union(geoms):
    accumulated_geom = geoms[0]
    for geom in geoms[1:]:
          accumulated_geom = cascaded_union([accumulated_geom, geom])
    if accumulated_geom.geom_type == 'Polygon':
          accumulated_geom = MultiPolygon([accumulated_geom])
    return accumulated_geom

# Union geometries
processed_cfs = []
for lst in cfs.values():
    obj = lst[0]
    obj['geometry'] = mapping(to_mp(better_union([shape(o['geometry']).buffer(0) for o in lst])))
    processed_cfs.append(obj)

with fiona.Env():
    with fiona.open('land_use.merged.json', 'w', **meta) as sink:
        for f in processed_cfs:
            sink.write(f)
```

Then merge all CFs into one file:

```
import os

meta = {
    "Maps for average CFs - occupation": [
        ("CF_AnnualCrops_Average_Occupation.shp", "occup_average_annual"),
        ("CF_ExtensiveForestry_Average_Occupation.shp", "occup_average_extensive"),
        ("CF_IntensiveForestry_Average_Occupation.shp", "occup_average_intensive"),
        ("CF_Pasture_Average_Occupation.shp", "occup_average_pasture"),
        ("CF_PermanentCrops_Average_Occupation.shp", "occup_average_permanent"),
        ("CF_Urban_Average_Occupation.shp", "occup_average_urban"),
    ],
    "Maps for marginal CFs - occupation": [
        ("CF_AnnualCrops_Marginal_Occupation.shp", "occup_marginal_annual"),
        ("CF_ExtensiveForestry_Marginal_Occupation.shp", "occup_marginal_extensive"),
        ("CF_IntensiveForestry_Marginal__Occupation.shp", "occup_marginal_intensive"),
        ("CF_Pasture_Marginal__Occupation.shp", "occup_marginal_pasture"),
        ("CF_PermanentCrops_Marginal_Occupation.shp", "occup_marginal_permanent"),
        ("CF_Urban_Marginal_Occupation.shp", "occup_marginal_urban"),
    ],
    "Maps for average CFs - transformation": [
        ("CF_AnnualCrops_Average_Transformation_TotalExtended.shp", "trans_average_annual"),
        ("CF_AnnualCrops_Average_Transformation_core_100ycut.shp", "trans_average_annual_100"),
        ("CF_ExtensiveForestry_Average_Transformation_TotalExtended.shp", "trans_average_extensive"),
        ("CF_ExtensiveForestry_Average_Transformation_core_100ycut.shp", "trans_average_extensive_100"),
        ("CF_IntensiveForestry_Average_Transformation_TotalExtended.shp", "trans_average_intensive"),
        ("CF_IntensiveForestry_Average_Transformation_core_100ycut.shp", "trans_average_intensive_100"),
        ("CF_Pasture_Average_Transformation_TotalExtended.shp", "trans_average_pasture"),
        ("CF_Pasture_Average_Transformation_core_100ycut.shp", "trans_average_pasture_100"),
        ("CF_PermanentCrops_Average_Transformation_TotalExtended.shp", "trans_average_permanent"),
        ("CF_PermanentCrops_Average_Transformation_core_100ycut.shp", "trans_average_permanent_100"),
        ("CF_Urban_Average_Transformation_TotalExtended.shp", "trans_average_urban"),
        ("CF_Urban_Average_Transformation_core_100ycut.shp", "trans_average_urban_100"),
    ],
    "Maps for marginal CFs - transformation": [
        ("CF_AnnualCrops_Marginal_Transformation_TotalExtended.shp", "trans_marginal_annual"),
        ("CF_AnnualCrops_Marginal_Transformation_core_100ycut.shp", "trans_marginal_annual_100"),
        ("CF_ExtensiveForestry_Marginal_Transformation_TotalExtended.shp", "trans_marginal_extensive"),
        ("CF_ExtensiveForestry_Marginal_Transformation_core_100ycut.shp", "trans_marginal_extensive_100"),
        ("CF_IntensiveForestry_Marginal_Transformation_TotalExtended.shp", "trans_marginal_intensive"),
        ("CF_IntensiveForestry_Marginal_Transformation_core_100ycut.shp", "trans_marginal_intensive_100"),
        ("CF_Pasture_Marginal_Transformation_TotalExtended.shp", "trans_marginal_pasture"),
        ("CF_Pasture_Marginal_Transformation_core_100ycut.shp", "trans_marginal_pasture_100"),
        ("CF_PermanentCrops_Marginal_Transformation_TotalExtended.shp", "trans_marginal_permanent"),
        ("CF_PermanentCrops_Marginal_Transformation_core_100ycut.shp", "trans_marginal_permanent_100"),
        ("CF_Urban_Marginal_Transformation_TotalExtended.shp", "trans_marginal_urban"),
        ("CF_Urban_Marginal_Transformation_core_100ycut.shp", "trans_marginal_urban_100"),
    ]
}


for dirpath, files in meta.items():
    for f in files:
        assert os.path.isfile(os.path.join("..", dirpath, f[0]))

cfs = {}

for dirpath, files in meta.items():
    for filename, column in files:
        print(filename)
        cfs[column] = {}
        fp = os.path.join("..", dirpath, filename)
        with fiona.open(fp) as src:
            for feat in src:
                cfs[column][feat['properties']['eco_code']] = float(feat['properties']['CF'] or 0.)

with fiona.Env():
    with fiona.open('land_use.merged.json') as source:
        meta = source.meta.copy()

        properties = dict(meta['schema']['properties'])
        del properties['CF']

        for column in cfs:
            properties[column] = 'float'

        meta['schema']['properties'] = properties

        with fiona.open("land_use.merged.all.json", "w", **meta) as sink:
            for feat in source:
                del feat['properties']['CF']
                for column, dct in cfs.items():
                    feat['properties'][column] = dct[feat['properties']['eco_code']]
                sink.write(feat)
```

Then convert to geopackage:

ogr2ogr -f GPKG land_use.gpkg land_use.merged.all.json
