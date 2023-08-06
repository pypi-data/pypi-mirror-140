from typing import Optional, List, Tuple

import xarray as xr
import numpy as np

from mpolar import interp, angle


def make(name: str,
         content: np.array,
         dimensions: List[Tuple[str, np.array]],
         unit: Optional[str] = None,
         dimension_units: Optional[List[str]] = None) -> xr.Dataset:
    # Note: Force every string to lower case
    attrs = {}
    if unit is not None:
        attrs["units"] = unit

    coords_dict = dict([(name.lower(), value) for name, value in dimensions])
    if dimension_units is not None:
        coords_dict = {}
        for (dim_name, dim_value), dim_unit in zip(dimensions, dimension_units):
            coords_dict[dim_name.lower()] = (dim_name.lower(), dim_value, {'units': dim_unit})

    return xr.DataArray(
        name=name.lower(),
        data=content,
        dims=[name.lower() for name, _ in dimensions],
        coords=coords_dict,
        attrs=attrs
    ).to_dataset()


def coordinates(ds: xr.Dataset) -> List[str]:
    return [str(coord) for coord in ds.coords]


def variables(ds: xr.Dataset) -> List[str]:
    coords = coordinates(ds)
    variables = []
    for v in ds.variables:
        if v in coords:
            continue
        variables.append(v)
    return variables


def evaluate(ds: xr.Dataset,
             variable_name: Optional[str] = None,
             extrapolate: Optional[interp.ExtrapolationType] = interp.ExtrapolationType.nearest,
             **kwargs) -> float:
    """Evaluate a polar at specific coordinates. Use a Nd linar interpolation
    to determine the value

    ```value = mpolar.evaluate(ds, power=1475, tws=12.44, twa=mpolar.Angle(-14.69))```

    :param ds: An xarray Dataset as obtained by the mpolar.parse function.
      If the dataset has more than one variable, the variable_name parameter
      should be specified
    :param variable_name: The variable to evaluate. None means the only available. Raises if more that one found
    :param extrapolate: The method to use for extrapolation. Defaults to nearest (no extrapolation)
    :param kwargs: coordinates to evaluate the variable at. For example, 'power=1475, tws=12.44'
    :return: the interplated value
    """
    # Deal with angle to be sure they are in range
    for key, value in kwargs.items():
        if isinstance(value, angle.Angle):
            kwargs[key] = value.degrees_for_coordinate(ds[key].values)

    # find the variable name if not set
    if variable_name is None:
        vars = variables(ds)
        if len(vars) != 1:
            raise Exception("Dataset has more than one variable. Please specify the variable to evaluate")
        variable_name = vars[0]

    # set the data
    coord_names = [str(v) for v in ds[variable_name].coords]
    if len(coord_names) != len(kwargs):
        raise Exception("Missing coordinate ({} needed, {} given)".format(coord_names, kwargs.keys()))

    coordinates = [None for _ in kwargs]  # initialize empty list with right number of coordinates
    ratio = [None for _ in kwargs]
    data = np.zeros(tuple([2 for _ in kwargs]))
    for key, value in kwargs.items():
        coord_index = coord_names.index(key)
        coord_values = ds[key].values
        coordinates[coord_index], ratio[coord_index] = interp.closest_indexes(coord_values, value, extrapolate)

    for index, elem in np.ndenumerate(data):
        data_index = [coordinates[coord_index][index_value] for coord_index, index_value in enumerate(list(index))]
        data[index] = ds[variable_name].values[tuple(data_index)]

    # run the interpolation
    while len(data.shape) != 1:
        # reduce the dimension by running the interpolation on the last one
        p1 = tuple([slice(2) for _ in data.shape[:-1]] + [0])
        p2 = tuple([slice(2) for _ in data.shape[:-1]] + [1])
        data = data[p1] * (1.0 - ratio[-1]) + data[p2] * ratio[-1]
        ratio = ratio[:-1]

    return data[0] * (1.0 - ratio[0]) + data[1] * ratio[0]
