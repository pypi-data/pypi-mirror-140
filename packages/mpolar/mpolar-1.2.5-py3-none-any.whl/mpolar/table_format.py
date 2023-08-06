from typing import Tuple, Optional
import re

import numpy as np
import xarray as xr

from mpolar.polar import make


def parse_unit(value: str) -> Tuple[float, str]:
    m = re.compile("(\d+(\.\d+)?)(\s+)?([^\d^\-^\s]+)?((\s+)?\-(\s+)?(\d+)(\%)?)?").match(value)
    if m is None:
        raise Exception("Invalid control format: {}".format(value))
    return float(m[1].strip()), (m[4].strip() if m.lastindex >= 4 else "")


def parse(path: str, sep: str = ";",
          column_name: str = "tws", column_unit: str = "kn",
          row_name: str = "twa", row_unit: str = "°",
          variable_name: Optional[str] = None, variable_unit: Optional[str] = None,
          control_name: Optional[str] = None, control_unit: Optional[str] = None) -> xr.Dataset:
    """Parse a table formatted polar

    Table formatted polars' origin are the sailing polar.
    It is a 2D table with True wind speed as columns, True wind angle as rows
    and boat speed as content.
    The format got enhanced by adding a control parameter. in the top left
    corner of that table and adding multiple tables (one per control) one next
    to the other separated by a column:

    | ```Control1;TWS1      ;...;TWSN      ; ;...; ;ControlN;TWS1      ;...;TWSN      ```
    | ```TWA1    ;value1-1-1;...;value1-1-N; ;...; ;TWA1    ;valueN-1-1;...;valueN-1-N```
    | ```...                                                                          ```
    | ```TWAN    ;value1-N-1;...;value1-N-N; ;...; ;TWAN    ;valueN-N-1;...;valueN-N-N```

    :param path: Path to the polar file
    :param sep: the separator of the CSV. Default to ';'
    :param column_name: The name of the column coordinate. Defaults to tws
    :param column_unit: The unit of the column coordinate. Defaults to kn
    :param row_name: The name of the row coordinate. Defaults to twa
    :param row_unit: The unit of the row coordinate. Defaults to °
    :param variable_name: The name of the content. If control name is power, default to speed. If control name is speed, default to power
    :param variable_unit: The name of the content. If variable_name is power, defaults to kW. Defaults to kn for speed
    :param control_name: The name of the control: If variable_name is power, default to speed. If variable_name is speed, default to power
    :param control_unit: The name of the content. If control_name is power, defaults to kW. Defaults to kn for speed
    :return: the xr.Dataset representing the polar
    """
    lines = []
    with open(path, "r") as f:
        for line in f.read().split("\n"):
            line = line.strip()
            if not line:
                continue
            lines.append(line)

    header = np.array(lines[0].split(sep))
    # remove empty characters from header
    for idx, element in enumerate(header):
        header[idx] = element.strip()

    # remove empty columns at the end
    while not header[-1]:
        header = header[:-1]

    indexes = np.argwhere(header == '').flatten()
    sizes = [(e - b) - 2 for b, e in zip(indexes[:-1], indexes[1:])]
    if not sizes:
        sizes = [len(header)]

    # columns
    column_count = sizes[0]
    if not np.all(np.array(sizes) == column_count):
        raise Exception("Every table size shouldn't vary (sizes: {})".format(sizes))
    a = [value for value in header[1:column_count + 1]]
    columns = [float(value) for value in header[1:column_count + 1]]

    # rows
    rows = [float(line.split(sep)[0]) for line in lines[1:]]

    # controls
    try:
        controls_string = header[[0] + list(indexes + 1)]
        controls_value_and_unit = [parse_unit(v) for v in controls_string]
        controls = [v for v, _ in controls_value_and_unit]
    except Exception as e:
        # if we can't load the controls, it might be because we are reading a sailing polar
        if len(sizes) > 1:
            raise e
        controls_value_and_unit = [(0, "kW")]
        controls = [0]

    if control_unit is None:
        control_units = [u for _, u in controls_value_and_unit]
        if not np.all(np.array(control_units) == control_units[0]):
            raise Exception("Control units should be constant (values found: {})".format(control_units))
        control_unit = control_units[0]

        if control_unit == '':  # Empty control unit
            if controls[-1] < 100:  # if control always bellow 100, either speed in knot of power in MW
                control_unit = 'kn'
            else:
                control_unit = "kW"

    if control_name is None:
        control_name = "stw"
        if control_unit == "kW":
            control_name = "power"

    # Variable name
    if variable_name is None:
        variable_name = "stw"
        if control_name == "stw":
            variable_name = "power"

    if variable_unit is None:
        variable_unit = "kn"
        if variable_name == "power":
            variable_unit = "kW"

    # content
    data = np.zeros((len(controls), len(rows), len(columns)))
    for index, _ in enumerate(controls):
        index_start = (index * (len(columns) + 2)) + 1
        index_end = index_start + len(columns)
        control_lines = [line.split(sep)[index_start:index_end] for line in lines[1:]]

        data[index, :, :] = np.array(control_lines).astype(np.float)

    return make(
        name=variable_name,
        unit=variable_unit,
        content=data,
        dimensions=[
            (control_name, controls),
            (row_name, rows),
            (column_name, columns)
        ],
        dimension_units=[
            control_unit,
            row_unit,
            column_unit
        ]
    )
