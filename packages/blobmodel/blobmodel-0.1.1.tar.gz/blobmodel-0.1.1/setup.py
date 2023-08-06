# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['blobmodel']

package_data = \
{'': ['*']}

install_requires = \
['black>=22.1.0,<23.0.0',
 'docformatter>=1.4,<2.0',
 'matplotlib>=3.5.1,<4.0.0',
 'mypy>=0.931,<0.932',
 'nptyping>=1.4.4,<2.0.0',
 'numpy>=1.22.2,<2.0.0',
 'pytest>=7.0.1,<8.0.0',
 'scipy>=1.8.0,<2.0.0',
 'tqdm>=4.62.3,<5.0.0',
 'xarray>=0.21.1,<0.22.0']

setup_kwargs = {
    'name': 'blobmodel',
    'version': '0.1.1',
    'description': 'Two dimensional model of propagating blobs',
    'long_description': '![Tests](https://github.com/uit-cosmo/2d_propagating_blobs/actions/workflows/workflow.yml/badge.svg)\n[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)\n[![codecov](https://codecov.io/gh/uit-cosmo/2d_propagating_blobs/branch/main/graph/badge.svg?token=QSS3BYQC6Y)](https://codecov.io/gh/uit-cosmo/2d_propagating_blobs)\n[![Sourcery](https://img.shields.io/badge/Sourcery-enabled-brightgreen)](https://sourcery.ai)\n# 2d_propagating_blobs\nTwo dimensional model of advecting and dissipating blobs.\n\nThe code has been deveoped originally to model profiles in the scrape-off layer of fusion experiments but it can be used to model any 2d system consisting of advecting pulses. An example is shown below:\n![Density evolution](readme_gifs/2d_blobs.gif ) \n\n## Installation\n\nDev install:\n```\ngit clone https://github.com/uit-cosmo/2d_propagating_blobs.git\ncd 2d_propagating_blobs\npip install -e .\n```\n\n\n## Usage\nCreate the grid on which the blobs are discretized with using the `Model` class. The `make_realization()` method computes the output as an xarray dataset which can also be written out as a `netcdf` file if the argument `file_name` is specified. A simple example is shown below:\n\n```Python\nfrom blobmodel import Model, show_model\n\nbm = Model(Nx=200, Ny=100, Lx=10, Ly=10, dt=0.1, T=20, blob_shape=\'gauss\',num_blobs=100)\n\nds = bm.make_realization(file_name="example.nc")\n```\nThe data can be shown as an animation using the `show_model` function:\n```Python\nshow_model(ds)\n```\nYou can specify the blob parameters with a BlobFactory class. The DefaultBlobFactory class has some of the most common distribution functions implemented. An example would look like this:\n```Python\nfrom blobmodel import Model, DefaultBlobFactory\n\n# use DefaultBlobFactory to define distribution functions fo random variables\nbf = DefaultBlobFactory(A_dist="exp", W_dist="uniform", vx_dist="deg", vy_dist="normal")\n\n# pass on bf when creating the Model\ntmp = Model(\n    Nx=100,\n    Ny=1,\n    Lx=10,\n    Ly=0,\n    dt=1,\n    T=1000,\n    blob_shape="exp",\n    t_drain=2,\n    periodic_y=False,\n    num_blobs=10000,\n    blob_factory=bf,\n)\n```\nAlternatively, you can specify all blob parameters exactly as you want by writing your own class which inherits from BlobFactory. See `examples/custom_blobfactory.py` as an example. \n## Input parameters\n### `Model()`\n- `Nx`: int, grid points in x\n- `Ny`: int, grid points in y\n- `Lx`: float, length of grid in x\n- `Ly`: float, length of grid in y\n- `dt`: float, time step \n- `T`: float, time length \n- `periodic_y`: bool, optional,\n            allow periodicity in y-direction \n- `blob_shape`: str, optional,\n            switch between `gauss` and `exp` blob\n- `num_blobs`: int, optional\n            number of blobs\n- `t_drain`: float, optional,\n            drain time for blobs \n- `blob_factory`: BlobFactory, optional,\n            object containing blob parameters\n- `labels`: bool, optional,\n            if True, field with blob labels is returned\n            used for creating training data for supervised machine learning algorithms\n- `label_border`: float, optional,\n            defines region of blob as region where density >= label_border * amplitude of Blob\n            only used if labels = True\n### `DefaultBlobFactory()`\n- `A_dist`: str, optional,\n            distribution of blob amplitudes\n- `W_dist`: str, optional,\n            distribution of blob widths\n- `vx_dist`: str, optinal,\n            distribution of blob velocities in x-dimension\n- `vy_dist`: str, optinal,\n            distribution of blob velocities in y-dimension\n- `A_parameter`: float, optional,\n            `free_parameter` for amplitudes\n- `W_parameter`: float, optional,\n            `free_parameter` for widths\n- `vx_parameter`: float, optional,\n            `free_parameter` for vx\n- `vy_parameter`: float, optional,\n            `free_parameter` for vy\n            \nThe following distributions are implemented:\n\n- `exp`: exponential distribution with mean 1\n- `gamma`: gamma distribution with `free_parameter` as shape parameter and mean 1\n- `normal`: normal distribution with zero mean and `free_parameter` as scale parameter\n- `uniform`: uniorm distribution with mean 1 and `free_parameter` as width\n- `ray`: rayleight distribution with mean 1\n- `deg`: array on ones\n- `zeros`: array of zeros\n### `make_realization()`\n- `file_name`: str, optional, \n            file name for .nc file containing data as xarray dataset\n- `speed_up`: bool, optional,\n            speeding up code by discretizing each single blob at smaller time window \n            when blob values fall under given error value the blob gets discarded \n\n            !!!  this is only a good approximation for blob_shape=\'exp\' !!!\n- `error`: float, optional,\n            numerical error at x = Lx when blob gets truncated \n### `show_model()`\n- `ds`: xarray Dataset,\n            Model data\n- `interval`: int, optional,\n            time interval between frames in ms\n- `save`: bool, optional,\n            if True save animation as gif\n- `gif_name`: str, optional,\n            set name for gif\n- `fps`: int, optional,\n            set fps for gif\n\n## Contact\nIf you have questions, suggestions or other comments you can contact me under gregor.decristoforo@uit.no\n\n',
    'author': 'gregordecristoforo',
    'author_email': 'gregor.decristoforo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/uit-cosmo/2d_propagating_blobs/blob/main/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
