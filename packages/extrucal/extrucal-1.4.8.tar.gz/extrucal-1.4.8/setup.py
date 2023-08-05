# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['extrucal']

package_data = \
{'': ['*']}

install_requires = \
['altair-saver>=0.5.0,<0.6.0',
 'ipykernel>=6.9.1,<7.0.0',
 'numpy>=1.22.2,<2.0.0',
 'pandas>=1.4.1,<2.0.0',
 'sphinx-autoapi>=1.8.4,<2.0.0',
 'sphinx-rtd-theme>=1.0.0,<2.0.0']

setup_kwargs = {
    'name': 'extrucal',
    'version': '1.4.8',
    'description': 'Provides functions for calculating various parameters in extrusion processes',
    'long_description': '[![ci-cd](https://github.com/johnwslee/extrucal/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/johnwslee/extrucal/actions/workflows/ci-cd.yml)\n[![codecov](https://codecov.io/gh/johnwslee/extrucal/branch/main/graph/badge.svg?token=YT37K0ESGF)](https://codecov.io/gh/johnwslee/extrucal)\n[![Documentation Status](https://readthedocs.org/projects/extrucal/badge/?version=latest)](https://extrucal.readthedocs.io/en/latest/index.html)\n![license status](https://img.shields.io/github/license/johnwslee/extrucal)\n\n# extrucal\n\n**Author:** John W.S. Lee\n\n`extrucal` provides functions that calculate throughputs and screw RPMs for various types of extrusion processes. Theoretical throughputs can be calculated by using the screw geometry and the processing condition, whereas the throughputs required for extruded products(cable, tube, rod, and sheet) can be calculated by using the product geometry. Based on these calculated throughputs, `extrucal` functions can generate tables and plots that show the processing windows considering extruder size, line speed, and screw RPM.\n\nA large portion of arguments for the functions are given the typical values. Some of the arguments for functions are as follows:\n screw size, channel depth, polymer melt density, screw RPM, screw pitch, flight width, number of flights, line speed, extruder size, etc.\n\n## Installation\n\n`extrucal` can be installed PyPI using the following terminal command:\n\n```bash\n$ pip install extrucal\n```\n\n## Package Functions\n\n**1. Functions in `extrucal.extrusion`**\n\n- `throughput_cal()`\n  - This function calculates the extrusion throughput (Drag Flow) given the screw size, RPM, the channel depth of metering channel, and screw pitch\n  \n- `throughput_table()`\n  - This function generates a table containing the extrusion throughput with respect to channel depth and screw RPM\n  \n- `throughput_plot()`\n  - This function generates a plot containing the extrusion throughput with respect to channel depth and screw RPM\n\n**2. Functions in `extrucal.cable_extrusion`**\n\n- `cable_cal()`\n  - This function calculates the required throughput for cables given the outer diameter, thickness, line speed, and solid polymer density\n  \n- `cable_table()`\n  - This function generate a table containing the required screw RPM with respect to line speed and extruder size\n  \n- `cable_plot()`\n  - This function generate a plot containing the required screw RPM with respect to line speed and extruder size\n\n**3. Functions in `extrucal.tube_extrusion`**\n\n- `tube_cal()`\n  - This function calculates the required throughput for tubes given the outer diameter, inner diameter, line speed, and solid polymer density\n  \n- `tube_table()`\n  - This function generate a table containing the required screw RPM with respect to line speed and extruder size\n  \n- `tube_plot()`\n  - This function generate a plot containing the required screw RPM with respect to line speed and extruder size\n\n**4. Functions in `extrucal.rod_extrusion`**\n\n- `rod_cal()`\n  - This function calculates the required throughput for rods given the outer diameter, line speed, solid polymer density, and number of die holes\n  \n- `rod_table()`\n  - This function generate a table containing the required screw RPM with respect to line speed and extruder size\n  \n- `rod_plot()`\n  - This function generate a plot containing the required screw RPM with respect to line speed and extruder size\n\n**5. Functions in `extrucal.sheet_extrusion`**\n\n- `sheet_cal()`\n  - This function calculates the required throughput for sheets given the width, thickness, line speed, solid polymer density, and number of die holes\n  \n- `sheet_table()`\n  - This function generate a table containing the required screw RPM with respect to line speed and extruder size\n  \n- `sheet_plot()`\n  - This function generate a plot containing the required screw RPM with respect to line speed and extruder size\n\n\n## Usage\n\n`extrucal` can be used to calculate extrusion throughput and to generate tables and plots of various parameters in extrusion processes\n\n```python\nfrom extrucal.extrusion import throughput_cal, throughput_table, throughput_plot\nfrom extrucal.cable_extrusion import cable_cal, cable_table, cable_plot\nfrom extrucal.tube_extrusion import tube_cal, tube_table, tube_plot\nfrom extrucal.rod_extrusion import rod_cal, rod_table, rod_plot\nfrom extrucal.sheet_extrusion import sheet_cal, sheet_table, sheet_plot\n```\n\n## Dependencies\n\n-   Python 3.9 and Python packages:\n\n    -   pandas==1.4.1\n    -   numpy==1.22.2\n    -   ipykernel==6.9.1\n    -   altair-saver==0.5.0\n\n## Documentation\n\nDocumentation `extrucal` can be found at [Read the Docs](https://extrucal.readthedocs.io/en/latest/index.html)\n\n## Contributing\n\nInterested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.\n\n## License\n\n`extrucal` was created by John Lee. It is licensed under the terms of the MIT license.\n\n## Credits\n\n`extrucal` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).\n',
    'author': 'John W.S. Lee',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/johnwslee/extrucal',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
