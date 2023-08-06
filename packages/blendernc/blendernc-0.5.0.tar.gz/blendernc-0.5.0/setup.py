# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['blendernc',
 'blendernc.core',
 'blendernc.core.lic',
 'blendernc.nodes',
 'blendernc.nodes.cmaps',
 'blendernc.nodes.grid',
 'blendernc.nodes.inputs',
 'blendernc.nodes.math',
 'blendernc.nodes.outputs',
 'blendernc.nodes.selecting',
 'blendernc.nodes.shortcuts']

package_data = \
{'': ['*'], 'blendernc': ['workspace/*']}

install_requires = \
['Bottleneck==1.2.1',
 'cfgrib>=0.9.9,<0.10.0',
 'click>=7,<8',
 'cmocean>=2.0,<3.0',
 'colorcet>=3.0.0,<4.0.0',
 'dask>=2021.8.1,<2022.0.0',
 'ecmwflibs>=0.4.5,<0.5.0',
 'matplotlib>=3.4.3,<4.0.0',
 'netCDF4>=1.5.7,<2.0.0',
 'numpy>=1.21.2,<2.0.0',
 'pooch>=1.5.1,<2.0.0',
 'psutil>=5.8.0,<6.0.0',
 'scipy>=1.7.1,<2.0.0',
 'toml>=0.10.2,<0.11.0',
 'toolz>=0.11.1,<0.12.0',
 'xarray>=0.19.0,<0.20.0',
 'zarr>=2.9.4,<3.0.0']

setup_kwargs = {
    'name': 'blendernc',
    'version': '0.5.0',
    'description': 'Blender add-on to import datasets (netCDF, grib, and zarr)',
    'long_description': '# BlenderNC\n\n![Read the Docs](https://img.shields.io/readthedocs/blendernc) ![Github CI](https://github.com/blendernc/blendernc/actions/workflows/test.yml/badge.svg) [![codecov](https://codecov.io/gh/blendernc/blendernc/branch/master/graph/badge.svg?token=NYJMMGIMPJ)](https://codecov.io/gh/blendernc/blendernc) [![Maintainability](https://api.codeclimate.com/v1/badges/bbd6f981e5f5a26c6a56/maintainability)](https://codeclimate.com/github/blendernc/blendernc/maintainability) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) ![GitHub](https://img.shields.io/github/license/blendernc/blendernc?color=lightblue) ![blender support](https://img.shields.io/badge/blender-2.83--2.93-blueviolet) ![GitHub release (latest by date)](https://img.shields.io/github/v/release/blendernc/blendernc?label=tag) [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/blendernc/blendernc/master.svg)](https://results.pre-commit.ci/latest/github/blendernc/blendernc/master) [![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/relekang/python-semantic-release)\n\n\n<!--INFO-->\n\n**BlenderNC** is an open source add-on and Python module to visualize **netCDF**, **grib**, and **zarr** datasets in [**Blender**](www.blender.org).\n\nBlenderNC builds upon [**xarray**](https://github.com/pydata/xarray) and [**dask**](https://dask.org) to lazy load, manipulate, and display datasets as images in Blender.\n\n#### Why BlenderNC?\n\nScience visualization is a fundamental part of science communication and the exploration of large datasets. However, production quality real-time visualization and animation of scientific data has remained unreachable to the scientific community. BlenderNC main goal is to facilitate the generation of quality animations of scientific gridded data with a powerful and simple interface. For example:\n\n- Quick load of datasets:\n\n<img src="https://raw.githubusercontent.com/blendernc/blendernc/master/docs/images/quick_load_gif.gif" width="70%" />\n\n- Nodes tree for more complex visualizations:\n\n<img src="https://raw.githubusercontent.com/blendernc/blendernc/master/docs/images/GEBCO_blendernc.png" width="70%" />\n\n- Math computations in BlenderNC node tree.\n\nDocumentation\n-------------\n\nLearn more about BlenderNC in the official documentation at [https://blendernc.readthedocs.io](https://blendernc.readthedocs.io)\n\nContributing\n------------\n\nAll contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome. More information about contributing to BlenderNC can be found at our [Contribution page](https://blendernc.readthedocs.io/en/latest/contribute.html).\n\nUse Github to:\n- report bugs,\n- suggest features,\n- provide examples,\n- and view the source code.\n\nSupport\n-------\n\n**BlenderNC** is supported by:\n\n<div style="width:100%">\n<a href="https://esowc.ecmwf.int">\n<img src="https://raw.githubusercontent.com/blendernc/blendernc/master/docs/images/logo_ESoWC.png" width="47%" style=\'margin-bottom:5px\' />\n</a>\n<a href="http://cosima.org.au/">\n<img src="https://raw.githubusercontent.com/blendernc/blendernc/master/docs/images/logo_cosima.png" width="47%" style=\'float:right;\'/>\n</a>\n</div>\n\nTo implement and improve support of weather and climate data visualizations in GRIB format and visualize numerical models of the global ocean and sea-ice.\n\n---\n\n#### Authors\n[@josuemtzmo](https://github.com/josuemtzmo)\n[@orioltinto](https://github.com/orioltinto)\n\n#### Contributors\n[@whatnick](https://github.com/whatnick)\n[@navidcy](https://github.com/navidcy)\n[@stephansiemen](https://github.com/stephansiemen)\n\n',
    'author': 'josuemtzmo',
    'author_email': 'josue.martinezmoreno@anu.edu.au',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/blendernc/blendernc',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
