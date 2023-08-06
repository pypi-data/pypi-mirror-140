from typing import Tuple
import re

import numpy as np
import xarray as xr
import pandas as pd

from mpolar.polar import make


def parse_unit(column_name: str) -> Tuple[str, str]:
    m = re.compile("(.*)\[(.*)\].*").match(column_name)
    if m is None:
        return column_name, ""
    # Note: forbidden ' ' char
    return m[1].strip().replace(" ", "_"), m[2].strip()


def parse(path: str, sep: str = ";") -> xr.Dataset:
    """Parse a list formatted polar

    A list formatted polar is a CSV with a header.
    Individual column header is formatted like 'name [unit]'
    The output variable is considered as the last column and all the others will
    be considered as coordinates in the same order

    :param path: Path to the polar file
    :param sep: The separator of the CSV. Default to ';'
    :return: the xr.Dataset representing the polar
    """
    df = pd.read_csv(path, sep=sep)
    df.dropna(how='all', axis=1, inplace=True)  # remove columns that are full of NaNs

    # remove rows that have NaN coordinates (NaN allowed in content)
    indexes = np.where(np.isnan(df.iloc[:, :-1].values).any(axis=1))
    df = df.drop(indexes[0])

    # we consider the N-1 first columns as coordinates. The last one is the content
    variable_col = df.columns.values[-1]
    coords = {v: np.unique(df[v].values) for v in df.columns.values[:-1]}

    # initialize content as zeros
    dims = tuple([len(values) for _, values in coords.items()])
    data = np.zeros(dims)

    # fill it up !
    for _, row in df.iterrows():
        index = tuple([np.where(values == float(row[name]))[0][0] for name, values in coords.items()])
        value = row[variable_col]
        # deal with comas instead of '.' in decimal numbers
        if isinstance(value, str):
            value = float(value.replace(",", "."))
        data[index] = value

    # create an xarray dataset from result
    variable_name, variable_unit = parse_unit(variable_col)
    coords_name_unit = {name: parse_unit(name) for name in coords.keys()}

    return make(
        name=variable_name,
        unit=variable_unit,
        content=data,
        dimensions=[(coords_name_unit[name][0], value) for name, value in coords.items()],
        dimension_units=[coords_name_unit[name][1] for name in coords.keys()],
    )
