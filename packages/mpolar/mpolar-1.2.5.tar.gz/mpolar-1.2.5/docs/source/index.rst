.. pympolar documentation master file, created by
   sphinx-quickstart on Fri Oct 15 11:12:31 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

====================================
Welcome to pympolar's documentation!
====================================

**pympolar** is a tool to ease the integration of ship performance tables.
It is designed to parse the classic formats and interpolate its values.

#######
Install
#######

.. code-block:: bash

  python -m pip install mpolar@git+ssh://git@d-ice.gitlab.host:/weather_routing/moro/pympolar.git@v0.1

###########
Basic Usage
###########

.. code-block:: python

  import mpolar

  p = mpolar.parse(...)
  value = mpolar.evaluate(p, power=7725.3715, tws=12.154, twa=mpolar.Angle(-12.4))



.. toctree::
   :maxdepth: 3
   :caption: Contents:

   parse
   evaluate
   plot


==================
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
