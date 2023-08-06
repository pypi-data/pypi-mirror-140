import xarray as xr
import numpy as np

import mpolar


def make_hybrid(ds: xr.Dataset) -> xr.Dataset:
    twa = np.arange(0, 360, 22.5)
    tws = np.array([0, 50])

    vars = mpolar.polar.variables(ds)
    if not vars:
        raise Exception("Couldn't find the polar variable")
    variable_name = vars[0]
    variable = ds[variable_name].values

    coordinate_name = mpolar.polar.coordinates(ds)[0]
    coordinate = ds[coordinate_name].values

    updated_variable = np.zeros((coordinate.shape[0], twa.shape[0], tws.shape[0]))
    for cidx, _ in enumerate(coordinate):
        for twaidx, _ in enumerate(twa):
            for twsidx, _ in enumerate(tws):
                updated_variable[cidx, twaidx, twsidx] = variable[cidx]

    return mpolar.polar.make(
        name=variable_name,
        content=updated_variable,
        dimensions=[(coordinate_name, coordinate), ("twa", twa), ("tws", tws)],
        unit=ds[variable_name].attrs.get("units", None),
        dimension_units=[
            ds[coordinate_name].attrs.get("units", ""),
            "°",
            "kn"
        ]
    )
