# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['fastoad_cs25',
 'fastoad_cs25.configurations',
 'fastoad_cs25.models',
 'fastoad_cs25.models.aerodynamics',
 'fastoad_cs25.models.aerodynamics.components',
 'fastoad_cs25.models.aerodynamics.components.resources',
 'fastoad_cs25.models.aerodynamics.components.utils',
 'fastoad_cs25.models.aerodynamics.external',
 'fastoad_cs25.models.aerodynamics.external.xfoil',
 'fastoad_cs25.models.aerodynamics.external.xfoil.resources',
 'fastoad_cs25.models.aerodynamics.external.xfoil.xfoil699',
 'fastoad_cs25.models.geometry',
 'fastoad_cs25.models.geometry.geom_components',
 'fastoad_cs25.models.geometry.geom_components.fuselage',
 'fastoad_cs25.models.geometry.geom_components.ht',
 'fastoad_cs25.models.geometry.geom_components.ht.components',
 'fastoad_cs25.models.geometry.geom_components.nacelle_pylons',
 'fastoad_cs25.models.geometry.geom_components.vt',
 'fastoad_cs25.models.geometry.geom_components.vt.components',
 'fastoad_cs25.models.geometry.geom_components.wing',
 'fastoad_cs25.models.geometry.geom_components.wing.components',
 'fastoad_cs25.models.geometry.profiles',
 'fastoad_cs25.models.geometry.profiles.resources',
 'fastoad_cs25.models.handling_qualities',
 'fastoad_cs25.models.handling_qualities.tail_sizing',
 'fastoad_cs25.models.loops',
 'fastoad_cs25.models.propulsion',
 'fastoad_cs25.models.propulsion.fuel_propulsion',
 'fastoad_cs25.models.propulsion.fuel_propulsion.rubber_engine',
 'fastoad_cs25.models.weight',
 'fastoad_cs25.models.weight.cg',
 'fastoad_cs25.models.weight.cg.cg_components',
 'fastoad_cs25.models.weight.cg.cg_components.load_cases',
 'fastoad_cs25.models.weight.mass_breakdown',
 'fastoad_cs25.models.weight.mass_breakdown.a_airframe',
 'fastoad_cs25.models.weight.mass_breakdown.b_propulsion',
 'fastoad_cs25.models.weight.mass_breakdown.c_systems',
 'fastoad_cs25.models.weight.mass_breakdown.d_furniture',
 'fastoad_cs25.models.weight.mass_breakdown.e_crew',
 'fastoad_cs25.notebooks',
 'fastoad_cs25.notebooks.01_tutorial',
 'fastoad_cs25.notebooks.01_tutorial.data',
 'fastoad_cs25.notebooks.01_tutorial.img',
 'fastoad_cs25.notebooks.02_CeRAS_case_study',
 'fastoad_cs25.notebooks.02_CeRAS_case_study.data',
 'fastoad_cs25.notebooks.02_CeRAS_case_study.img']

package_data = \
{'': ['*']}

install_requires = \
['fast-oad>=1.3.0,<2.0.0',
 'numpy>=1.17.3,<2.0.0',
 'openmdao>=3.10,<4.0',
 'pandas>=1.1.0,<2.0.0',
 'scipy>=1.4.1,<2.0.0',
 'stdatm>=0.1.0,<0.2.0']

entry_points = \
{'fastoad.plugins': ['cs25 = fastoad_cs25']}

setup_kwargs = {
    'name': 'fast-oad-cs25',
    'version': '0.1.1',
    'description': 'FAST-OAD_CS25 is a FAST-OAD plugin with CS25/FAR25-related models.',
    'long_description': '![Tests](https://github.com/fast-aircraft-design/FAST-OAD_CS25/workflows/Tests/badge.svg)\n[![Documentation Status](https://readthedocs.org/projects/fast-oad-cs25/badge/?version=stable)](https://fast-oad.readthedocs.io/)\n\n[![Codacy Badge](https://app.codacy.com/project/badge/Grade/06d1fb8ee5c3429cb3cbb165413187bc)](https://www.codacy.com/gh/fast-aircraft-design/FAST-OAD_CS25/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=fast-aircraft-design/FAST-OAD_CS25&amp;utm_campaign=Badge_Grade)\n[![codecov](https://codecov.io/gh/fast-aircraft-design/FAST-OAD_CS25/branch/main/graph/badge.svg?token=91CIX996RD)](https://codecov.io/gh/fast-aircraft-design/FAST-OAD_CS25)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)\n\n[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/fast-aircraft-design/FAST-OAD_CS25.git/latest-release?urlpath=lab%2Ftree%2Fsrc%2Ffastoad%2Fnotebooks)\n\n\nFAST-OAD CS-25/FAR-25-related models\n====================================\n\nThis package is a plugin for FAST-OAD (version 1.3 or above). It contains models related to classic\ncommercial transport aircraft.\n\nWant to try quickly?\n--------------------\nYou can run FAST-OAD-CS25 notebooks **without installation** using our\n[Binder-hosted Jupyter notebooks](https://mybinder.org/v2/gh/fast-aircraft-design/FAST-OAD_CS25.git/latest-release?filepath=src%2Ffastoad%2Fnotebooks).\n\n\nInstall\n-------\n\n**Prerequisite**:FAST-OAD needs at least **Python 3.7.0**.\n\nIt is recommended (but not required) to do the install in a virtual\nenvironment ([conda](https://docs.conda.io/en/latest/),\n[venv](https://docs.python.org/3.7/library/venv.html), ...)\n\nOnce Python is installed, installation can be done using pip. FAST-OAD, the core software, will be\ninstalled at the same time.\n\n> **Note**: If your network uses a proxy, you may have to do [some\n> settings](https://pip.pypa.io/en/stable/user_guide/#using-a-proxy-server)\n> for pip to work correctly\n\nYou can install the latest version (including the main software FAST-OAD) with this command:\n\n``` {.bash}\n$ pip install --upgrade fast-oad-cs25\n```\n',
    'author': 'Christophe DAVID',
    'author_email': 'christophe.david@onera.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fast-aircraft-design/FAST-OAD',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
