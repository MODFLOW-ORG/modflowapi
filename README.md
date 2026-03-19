# modflowapi

[![CI](https://github.com/MODFLOW-ORG/modflowapi/actions/workflows/ci.yml/badge.svg)](https://github.com/MODFLOW-ORG/modflowapi/actions/workflows/ci.yml)
[![GitHub contributors](https://img.shields.io/github/contributors/MODFLOW-ORG/modflowapi)](https://img.shields.io/github/contributors/MODFLOW-ORG/modflowapi)
[![GitHub tag](https://img.shields.io/github/tag/MODFLOW-ORG/modflowapi.svg)](https://github.com/MODFLOW-ORG/modflowapi/tags/latest)

[![PyPI License](https://img.shields.io/pypi/l/modflowapi)](https://pypi.python.org/pypi/modflowapi)
[![PyPI Status](https://img.shields.io/pypi/status/modflowapi.png)](https://pypi.python.org/pypi/modflowapi)
[![PyPI Format](https://img.shields.io/pypi/format/modflowapi)](https://pypi.python.org/pypi/modflowapi)
[![PyPI Version](https://img.shields.io/pypi/v/modflowapi.png)](https://pypi.python.org/pypi/modflowapi)
[![PyPI Versions](https://img.shields.io/pypi/pyversions/modflowapi.png)](https://pypi.python.org/pypi/modflowapi)

[![Anaconda License](https://anaconda.org/conda-forge/modflowapi/badges/license.svg)](https://anaconda.org/conda-forge/modflowapi/badges/license.svg)
[![Anaconda Version](https://anaconda.org/conda-forge/modflowapi/badges/version.svg)](https://anaconda.org/conda-forge/modflowapi)
[![Anaconda Updated](https://anaconda.org/conda-forge/modflowapi/badges/latest_release_date.svg)](https://anaconda.org/conda-forge/modflowapi)

An extension to [xmipy](https://pypi.org/project/xmipy/) for the [MODFLOW API](https://www.usgs.gov/publications/modflow-application-programming-interface-simulationcontrol-and-software).

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
- [Installation](#installation)
- [Documentation](#documentation)
- [Citation](#citation)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Introduction

The `modflowapi` Python package can be used to access functionality in the eXtended Model Interface (XMI) wrapper (XmiWrapper) 
and additional functionality specific to the MODFLOW API. Currently it is a joint development of the USGS and Deltares.

## Installation

`modflowapi` requires Python 3.10+, with:

```shell
numpy
pandas
xmipy
```

To install `modflowapi` with pip:

```
pip install modflowapi
```

Or with conda:

```
conda install -c conda-forge modflowapi
```

## Documentation

Documentation is available [on ReadTheDocs](modflowapi.readthedocs.io).

Examples using `modflowapi` and its extensions can be found in the [Quickstart](docs/examples/notebooks/Quickstart.ipynb) and the [Extensions](docs/examples/notebooks/MODFLOW-API_extensions_objects.ipynb) notebooks. An example of using the MODFLOW API to monitor heads during a simulation can be found in the [Head Monitor Example](docs/examples/notebooks/Head_Monitor_Example.ipynb) Notebook. 

For more info on MODFLOW 6 see [the USGS overview](https://water.usgs.gov/ogw/modflow/).

## Citation

Hughes, Joseph D., Russcher, M. J., Langevin, C. D., Morway, E. D. and McDonald, R. R., 2022, The MODFLOW Application Programming Interface for simulationcontrol and software interoperability: Environmental Modelling & Software, v. 148, p. 105257, [doi:10.1016/j.envsoft.2021.105257](https://doi.org/10.1016/j.envsoft.2021.105257).

### ***Papers featuring the MODFLOW 6 API***

[White, J.T., Ewing, J.E., Ruskauff, G., and Rashid, H., 2023. A generic closed-loop contaminant treatment system package for MODFLOW 6. Groundwater v. 61, no. 1: 131–138. https://doi.org/10.1111/gwat.13239.](https://doi.org/10.1111/gwat.13239)

[Larsen, J.D., Langevin, C.D., Hughes, J.D. and Niswonger, R.G., 2024. An Agricultural Package for MODFLOW 6 using the application programming interface. Groundwater v. 62, no. 1: 157-166. https://doi.org/10.1111/gwat.13367.](https://doi.org/10.1111/gwat.13367)

[Hayek, M., White, J.T., Markovich, K.H., Hughes, J.D., Lavenue, M., 2025. MF6-ADJ: A non-intrusive adjoint sensitivity capability for MODFLOW 6. Groundwater v. 63, no. 6: 874-888. https://doi.org/10.1111/gwat.70025.](https://doi.org/10.1111/gwat.70025)

[Perez-Illanes, R., Langevin, C.D., Muniruzzaman, M., Rolle, M., 2026. Incorporating electrostatic coupling effects into multispecies solute transport simulations with MODFLOW. Groundwater v. 64, no. 2: 210-222. https://doi.org/10.1111/gwat.70033.](https://doi.org/10.1111/gwat.70033)

