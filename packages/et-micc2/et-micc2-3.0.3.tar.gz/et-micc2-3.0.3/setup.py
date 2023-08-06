# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['et_micc2',
 'et_micc2.scripts',
 'et_micc2.templates.app-single-command.{{tmpl.project_name}}.tests',
 'et_micc2.templates.app-single-command.{{tmpl.project_name}}.{{tmpl.package_name}}',
 'et_micc2.templates.app-sub-commands.{{tmpl.project_name}}.tests',
 'et_micc2.templates.app-sub-commands.{{tmpl.project_name}}.{{tmpl.package_name}}',
 'et_micc2.templates.submodule-cpp-test.{{tmpl.module_name}}',
 'et_micc2.templates.submodule-f90-test.{{tmpl.module_name}}',
 'et_micc2.templates.submodule-py-test.{{tmpl.module_name}}',
 'et_micc2.templates.submodule-py.{{tmpl.module_name}}',
 'et_micc2.templates.top-level-package.{{tmpl.project_name}}.docs',
 'et_micc2.templates.top-level-package.{{tmpl.project_name}}.tests',
 'et_micc2.templates.top-level-package.{{tmpl.project_name}}.tests.{{tmpl.package_name}}',
 'et_micc2.templates.top-level-package.{{tmpl.project_name}}.{{tmpl.package_name}}']

package_data = \
{'': ['*'],
 'et_micc2': ['templates/submodule-cpp/{{tmpl.module_name}}/*',
              'templates/submodule-f90/{{tmpl.module_name}}/*',
              'templates/top-level-package/{{tmpl.project_name}}/*']}

install_requires = \
['click>=7.0,<8.0',
 'pypi-simple>=0.8.0,<0.9.0',
 'semantic_version>=2.8.3,<3.0.0',
 'tomlkit>=0.7.0,<0.8.0',
 'walkdir>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['micc2 = et_micc2:cli_micc.main']}

setup_kwargs = {
    'name': 'et-micc2',
    'version': '3.0.3',
    'description': 'A practical Python project skeleton generator.',
    'long_description': "*****\nMicc2\n*****\n\n.. image:: https://img.shields.io/pypi/v/et-micc2.svg\n        :target: https://pypi.python.org/pypi/et-micc2\n\n.. image:: https://readthedocs.org/projects/et-micc2/badge/?version=latest\n        :target: https://et-micc2.readthedocs.io/en/latest/?badge=latest\n        :alt: Documentation Status\n\n`Micc2_ <https://github.com/etijskens/et-micc2>`_ is a Python project manager: it helps\nyou organize your Python project from simple single file modules to fully fledged \nPython packages containing modules, sub-modules, apps and binary extension modules \nwritten in Fortran or C++. Micc2_ organizes your project in a way that is considered good\npractice by a large part of the Python community. \n\n* Micc2_ helps you create new projects. You can start small with a simple one-file \n  package and add material as you go, such as:\n  \n  * Python **sub-modules** and **sub-packages**,\n  * **applications**, also known as command line interfaces (CLIs). \n  * **binary extension modules** written in C++ and Fortran. Boiler plate code is \n    automatically added as to build these binary extension with having to go through\n    al the details. This is, in fact, the foremost reason that got me started on this\n    project: For *High Performance Python* it is essential to rewrite slow and \n    time consuming parts of a Python script or module in a language that is made \n    for High Performance Computing. As figuring out how that can be done, requires \n    quite some effort, Micc2_ was made to automate this part while maintaining the \n    flexibility. \n  * Micc2_ adds typically files containing example code that shows you how to add your\n    own functionality.\n    \n* You can automatically **extract documentation** from the doc-strings of your files,\n  and build html documentation that you can consult in your browser, or a .pdf \n  documentation file.\n* With a little extra effort the generated html **documentation is automatically published** \n  to `readthedocs <https://readthedocs.org>`_.\n* Micc2_ helps you with **version management and control**.\n* Micc2_ helps you with **testing** your code.\n* Micc2_ helps you with **publishing** your code to e.g. `PyPI <https://pypi.org>`_, so\n  that you colleagues can use your code by simply running::\n\n    > pip install your_nifty_package\n\nCredits\n-------\nMicc2_ does not do all of this by itself. For many things it relies on other strong \nopen source tools. Here is a list of tools micc2_ is using or cooperating with happily:\n\n*   `Pyenv <https://github.com/pyenv/pyenv>`_: management of different Python versions on your desktop.\n*   `Poetry <https://python-poetry.org>`_ for packaging and publishing.\n*   `Git <https://www.git-scm.com/>`_ for version control.\n*   `Pytest <https://www.git-scm.com/>`_ for testing your code.\n*   `Sphinx <http://www.sphinx-doc.org/>`_ to extract documentation from your project's\n    doc-strings.\n*   `CMake <https://cmake.org>`_ is used for building binary extension modules written\n    in C++ and Fortran.\n*   `F2py <https://docs.scipy.org/doc/numpy/f2py/>`_ for transforming modern Fortran code\n    into performant binary extension modules interfacing nicely with numpy arrays.\n*   `Pybind11 <https://pybind11.readthedocs.io/en/stable/>`_ as the glue between C++ source\n    code and performant binary extension modules, also interfacing nicely with numpy arrays.\n\nRoadmap\n=======\nThese features are still on our wish list:\n\n* Contininous integtration (CI)\n* Code style, e.g. `flake8 <http://flake8.pycqa.org/en/latest/>`_ or `black <https://github.com/psf/black>`_\n* Profiling\n* Gui for debugging C++/Fortran binary extensions\n* Micc2 projects on Windows (So far, only support on Linux and MacOS).\n\n",
    'author': 'Engelbert Tijskens',
    'author_email': 'engelbert.tijskens@uantwerpen.be',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/etijskens/et-micc2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
