# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['imktk', 'imktk.dataarray_methods']

package_data = \
{'': ['*'], 'imktk': ['dataset_methods/*']}

install_requires = \
['netCDF4>=1.5.8,<2.0.0', 'xarray>=0.20.1,<0.21.0']

entry_points = \
{'console_scripts': ['imktk = imktk:main']}

setup_kwargs = {
    'name': 'imktk',
    'version': '0.1.8rc1',
    'description': 'Toolkit provided by IMK at KIT',
    'long_description': '# IMK Toolkit\n\nThis toolkit provides post-processing scripts developed by members of the\n[Institute of Meteorology and Climate Research (IMK)](https://dev.to/epassaro/keep-your-research-reproducible-with-conda-pack-and-github-actions-339n)\nat the Karlsruhe Institute of Technology (KIT). The goal of this module is to\ngather together python post-processing scripts for the analysis of netCDF data.\n\n## Getting Started\nThe easiest method to test the module before installation is to use the\nprovided  [`Dockerfile`](/Dockerfile) (together with [`Makefile`](/Makefile)).\n\nBuild the container\n```bash\ndocker build --tag imktk/imktk .\n# or\nmake container\n```\n\nEnter the container\n```bash\ndocker run -it -v $(pwd)/imktk:/home/python/imktk imktk/imktk bash\n# or\nmake bash\n```\n> Changes to the repository are directly reflected within the container.\n> Therefore, this method is **recommended for development purposes**.\n> For details see [`CONTRIBUTING.md`](/CONTRIBUTING.md)\n\n## Install\n\nChoose one of the following methods to install the package:\n\n1. Install using `pip`\n2. Install using `conda`\n3. Install straight from this repository using `git clone`\n\nThis package supports `Python3` starting with version `3.7`. If you are using\nan earlier version of `Python` please consider updating your system.\n\n### `pip`\n\nReleases are automatically uploaded to PyPI. Please execute following command\nto install the package.\n\n```\npython3 -m pip install imktk\n```\n\n### `conda`\n\nCurrently the package does no support native installation using `conda`\nrespectively `conda-forge`. This feature is on the roadmap and you can follow\nits process using issue [#34](https://github.com/imk-toolkit/imk-toolkit/issues/34).\nThe current workaround for `conda` installation is to use the following steps\nfor any given environment `<env>`.\n\n1. Activate the environment\n```bash\nconda activate <env>\n```\n2. Install using `pip`\n```bash\npython3 -m pip install imktk\n```\n\n### `git clone`\n\nIt is also possible to install the package natively by cloning the repository.\nIf you are interested in using this method of installation please follow\nthese steps\n\n1. Install build dependencies\n```bash\npython3 -m pip install build\n```\n\n2. Clone repository\n\n```bash\ngit clone https://github.com/imk-toolkit/imk-toolkit.git\n```\n\n3. Generate the Python packages\n\n```bash\npython3 -m build\n# or\nmake\n# or\nmake build\n```\n\n4. Install packages\n\n```bash\npip3 install dist/imktk-<current.version>-py3-none-any.whl\n# or\nmake install\n```\n\nPlease be aware that the package uses `HDF5` and `netCDF` c-library in the\nbackend. If you are installing using this method consider setting the\n`HDF5_DIR` environment variable with the location of the HDF5 header files.\n\n\n## Usage\n\n```python\nimport imktk\nimport xarray as xr\n\nt = xr.tutorial.open_dataset("rasm").load().Tair\nanomaly_free_t = t.imktk.anomalies()\n```\n\n## Further reading\nIf you are interested in the inner workings of the package and details of the\nimplementation please refer to the embedded [README.md](/imktk/README.md).\n',
    'author': 'Uğur Çayoğlu',
    'author_email': 'Ugur.Cayoglu@kit.edu',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/imk-toolkit/imk-toolkit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
