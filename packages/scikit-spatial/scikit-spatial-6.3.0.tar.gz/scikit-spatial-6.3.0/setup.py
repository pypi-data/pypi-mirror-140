# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['skspatial', 'skspatial.objects']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3,<4', 'numpy>=1.20,<2.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=1,<2'],
 'base_test': ['pytest==6.2.2', 'pytest-cov==2.11.1'],
 'docs': ['Sphinx==4.2.0',
          'numpydoc==1.1.0',
          'sphinx-bootstrap-theme==0.8.0',
          'sphinx-gallery==0.9.0'],
 'pre_commit': ['pre-commit==2.11.1'],
 'property': ['hypothesis==6.8.1']}

setup_kwargs = {
    'name': 'scikit-spatial',
    'version': '6.3.0',
    'description': 'Spatial objects and computations based on NumPy arrays.',
    'long_description': '\n.. figure:: images/logo.svg\n         :align: left\n         :width: 70%\n\n.. image:: https://img.shields.io/pypi/v/scikit-spatial.svg\n         :target: https://pypi.python.org/pypi/scikit-spatial\n\n.. image:: https://anaconda.org/conda-forge/scikit-spatial/badges/version.svg\n         :target: https://anaconda.org/conda-forge/scikit-spatial\n\n.. image:: https://img.shields.io/pypi/pyversions/scikit-spatial.svg\n         :target: https://pypi.python.org/pypi/scikit-spatial\n\n.. image:: https://github.com/ajhynes7/scikit-spatial/actions/workflows/main.yml/badge.svg\n         :target: https://github.com/ajhynes7/scikit-spatial/actions/workflows/main.yml\n\n.. image:: https://results.pre-commit.ci/badge/github/ajhynes7/scikit-spatial/master.svg\n   :target: https://results.pre-commit.ci/latest/github/ajhynes7/scikit-spatial/master\n   :alt: pre-commit.ci status\n\n.. image:: https://readthedocs.org/projects/scikit-spatial/badge/?version=latest\n         :target: https://scikit-spatial.readthedocs.io/en/latest/?badge=latest\n         :alt: Documentation Status\n\n.. image:: https://codecov.io/gh/ajhynes7/scikit-spatial/branch/master/graph/badge.svg\n         :target: https://codecov.io/gh/ajhynes7/scikit-spatial\n\n|\n\nIntroduction\n------------\n\nThis package provides spatial objects based on NumPy arrays, as well as computations using these objects. The package includes computations for 2D, 3D, and higher-dimensional space.\n\nThe following spatial objects are provided:\n\n   - Point\n   - Points\n   - Vector\n   - Line\n   - Plane\n   - Circle\n   - Sphere\n   - Triangle\n   - Cylinder\n\nMost of the computations fall into the following categories:\n\n   - Measurement\n   - Comparison\n   - Projection\n   - Intersection\n   - Fitting\n   - Transformation\n\nAll spatial objects are equipped with plotting methods based on ``matplotlib``. Both 2D and 3D plotting are supported. Spatial computations can be easily visualized by plotting multiple objects at once.\n\n\nWhy this instead of ``scipy.spatial`` or ``sympy.geometry``?\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\nThis package has little to no overlap with the functionality of ``scipy.spatial``. It can be viewed as an object-oriented extension.\n\nWhile similar spatial objects and computations exist in the ``sympy.geometry`` module, ``scikit-spatial`` is based on NumPy rather than symbolic math. The primary objects of ``scikit-spatial`` (``Point``, ``Points``, and ``Vector``) are actually subclasses of the NumPy *ndarray*. This gives them all the regular functionality of the *ndarray*, plus additional methods from this package.\n\n>>> from skspatial.objects import Vector\n\n>>> vector = Vector([2, 0, 0])\n\nBehaviour inherited from NumPy:\n\n>>> vector.size\n3\n>>> vector.mean().round(3)\n0.667\n\nAdditional methods from ``scikit-spatial``:\n\n>>> vector.norm()\n2.0\n>>> vector.unit()\nVector([1., 0., 0.])\n\n``Point`` and ``Vector`` are based on a 1D NumPy array, and ``Points`` is based on a 2D NumPy array, where each row represents a point in space.  The ``Line`` and ``Plane`` objects have ``Point`` and ``Vector`` objects as attributes.\n\nNote that most methods inherited from NumPy return a regular *ndarray*, instead of the spatial object class.\n\n>>> vector.sum()\narray(2)\n\nThis is to avoid getting a spatial object with a forbidden shape, like a zero dimension ``Vector``. Trying to convert this back to a ``Vector`` causes an exception.\n\n>>> Vector(vector.sum())\nTraceback (most recent call last):\n...\nValueError: The array must be 1D.\n\n\nBecause the computations of ``scikit-spatial`` are also based on NumPy, keyword arguments can be passed to NumPy functions. For example, a tolerance can be specified while testing for collinearity. The ``tol`` keyword is passed to ``numpy.linalg.matrix_rank``.\n\n>>> from skspatial.objects import Points\n\n>>> points = Points([[1, 2, 3], [4, 5, 6], [7, 8, 8]])\n\n>>> points.are_collinear()\nFalse\n>>> points.are_collinear(tol=1)\nTrue\n\n\n\nInstallation\n------------\n\nThe package can be installed with pip.\n\n.. code-block:: bash\n\n   $ pip install scikit-spatial\n\n\nIt can also be installed with conda.\n\n.. code-block:: bash\n\n   $ conda install scikit-spatial -c conda-forge\n\n\nExample Usage\n-------------\n\nMeasurement\n~~~~~~~~~~~\n\nMeasure the cosine similarity between two vectors.\n\n>>> from skspatial.objects import Vector\n\n>>> Vector([1, 0]).cosine_similarity([1, 1]).round(3)\n0.707\n\n\nComparison\n~~~~~~~~~~\n\nCheck if multiple points are collinear.\n\n>>> from skspatial.objects import Points\n\n>>> points = Points([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])\n\n>>> points.are_collinear()\nTrue\n\n\nProjection\n~~~~~~~~~~\n\nProject a point onto a line.\n\n>>> from skspatial.objects import Line\n\n>>> line = Line(point=[0, 0, 0], direction=[1, 1, 0])\n\n>>> line.project_point([5, 6, 7])\nPoint([5.5, 5.5, 0. ])\n\n\nIntersection\n~~~~~~~~~~~~\n\nFind the intersection of two planes.\n\n>>> from skspatial.objects import Plane\n\n>>> plane_a = Plane(point=[0, 0, 0], normal=[0, 0, 1])\n>>> plane_b = Plane(point=[5, 16, -94], normal=[1, 0, 0])\n\n>>> plane_a.intersect_plane(plane_b)\nLine(point=Point([5., 0., 0.]), direction=Vector([0, 1, 0]))\n\n\nAn error is raised if the computation is undefined.\n\n>>> plane_b = Plane(point=[0, 0, 1], normal=[0, 0, 1])\n\n>>> plane_a.intersect_plane(plane_b)\nTraceback (most recent call last):\n...\nValueError: The planes must not be parallel.\n\n\nFitting\n~~~~~~~\n\nFind the plane of best fit for multiple points.\n\n>>> points = [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]]\n\n>>> Plane.best_fit(points)\nPlane(point=Point([0.5, 0.5, 0. ]), normal=Vector([0., 0., 1.]))\n\n\nTransformation\n~~~~~~~~~~~~~~\n\nTransform multiple points to 1D coordinates along a line.\n\n>>> line = Line(point=[0, 0, 0], direction=[1, 2, 0])\n>>> points = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\n\n>>> line.transform_points(points).round(3)\narray([ 2.236,  6.261, 10.286])\n\n\nAcknowledgment\n--------------\n\nThis package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.\n\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage\n',
    'author': 'Andrew Hynes',
    'author_email': 'andrewjhynes@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ajhynes7/scikit-spatial',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
