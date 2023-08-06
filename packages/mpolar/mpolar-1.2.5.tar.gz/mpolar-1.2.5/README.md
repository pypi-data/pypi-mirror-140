# pympolar: A package to parse and evaluate polar tables for marine navigation

Supported formats:
* List: A csv with a header. The following will create a polar like f(power, tws, twa) = stw
```
power [kW];tws[kn];twa[°];stw[kn]
100;0;0;5
...
```

* Table

## Install

```bash
python -m pip install mpolar@git+ssh://git@d-ice.gitlab.host:/weather_routing/moro/pympolar.git@v0.8
```
