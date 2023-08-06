from typing import List, Optional

import xarray as xr
import numpy as np

import plotly.graph_objects as go

import mpolar


def show_sailing(ds: xr.Dataset,
                 tws_coordinate_name: str = "tws",
                 tws: Optional[List[float]] = None,
                 twa_coordinate_name: str = "twa",
                 twa: Optional[List[float]] = None):
    raise Exception("To Be Developped !")


def show_hybrid(ds: xr.Dataset,
                control_name: str,
                controls: Optional[List[float]] = None,
                tws_coordinate_name: str = "tws",
                tws: Optional[List[float]] = None,
                twa_coordinate_name: str = "twa",
                twa: Optional[List[float]] = None):
    default_control_index = 0

    if controls is None:
        controls = ds[control_name].values
    if tws is None:
        tws = ds[tws_coordinate_name].values
    if twa is None:
        twa = ds[twa_coordinate_name].values

    variable_name = mpolar.polar.variables(ds)[0]

    fig = go.Figure()
    for control in controls:
        for wind_speed in tws:
            values = [mpolar.evaluate(ds, **{control_name: control, tws_coordinate_name: wind_speed, twa_coordinate_name: mpolar.Angle(wind_angle)}) for wind_angle in twa]
            fig.add_trace(go.Scatterpolar(
                name="{}kn".format(wind_speed),
                r=values,
                theta=twa,
                mode="lines",
                visible=(control == controls[default_control_index]),
                hovertext=["{}° => {}{}".format(angle, value, ds[variable_name].attrs.get("units", "")) for value, angle in zip(values, twa)]
            ))

    buttons = [
        dict(
            method='update',
            label="{}: {}{}".format(control_name, control, ds[control_name].attrs.get("units", "")),
            args=[
                {
                    'visible': np.array([
                        [control == other_control for _ in tws]
                        for other_control in controls
                    ]).flatten()
                }
            ]
        )
        for control in controls
    ]

    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                rotation=90,
                direction="clockwise"
            ),
        ),
        updatemenus=[
            {"buttons": buttons, "direction": "down", "active": 0, "showactive": True,
             "x": 0.5, "y": 1.15}]
    )

    fig.show()


def show_propulsion(ds: xr.Dataset,
                    tws_coordinate_name: str = "tws",
                    tws: Optional[List[float]] = None,
                    twa_coordinate_name: str = "twa",
                    twa: Optional[List[float]] = None,
                    controls: Optional[List[float]] = None):
    control_name = None
    for coordinate in ds.coords:
        if coordinate not in [tws_coordinate_name, twa_coordinate_name]:
            control_name = str(coordinate)

    if control_name is None:
        return show_sailing(ds, tws_coordinate_name, tws, twa_coordinate_name, twa)

    return show_hybrid(ds, control_name, controls, tws_coordinate_name, tws, twa_coordinate_name, twa)

