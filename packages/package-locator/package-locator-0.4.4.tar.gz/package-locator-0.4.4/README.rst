package-locator
===========================

|PyPI| |Python Version| |License| |Read the Docs| |Build| |Tests| |Codecov| |pre-commit| |Black|

.. |PyPI| image:: https://img.shields.io/pypi/v/package-locator.svg
   :target: https://pypi.org/project/package-locator/
   :alt: PyPI
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/package-locator
   :target: https://pypi.org/project/package-locator
   :alt: Python Version
.. |License| image:: https://img.shields.io/github/license/nasifimtiazohi/package-locator
   :target: https://opensource.org/licenses/MIT
   :alt: License
.. |Read the Docs| image:: https://img.shields.io/readthedocs/package-locator/latest.svg?label=Read%20the%20Docs
   :target: https://package-locator.readthedocs.io/
   :alt: Read the documentation at https://package-locator.readthedocs.io/
.. |Build| image:: https://github.com/nasifimtiazohi/package-locator/workflows/Build%20package-locator%20Package/badge.svg
   :target: https://github.com/nasifimtiazohi/package-locator/actions?workflow=Package
   :alt: Build Package Status
.. |Tests| image:: https://github.com/nasifimtiazohi/package-locator/workflows/Run%20package-locator%20Tests/badge.svg
   :target: https://github.com/nasifimtiazohi/package-locator/actions?workflow=Tests
   :alt: Run Tests Status
.. |Codecov| image:: https://codecov.io/gh/nasifimtiazohi/package-locator/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/nasifimtiazohi/package-locator
   :alt: Codecov
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black


Features
--------

* For a given package, package-locator locates its source code repository and the sub-directory within the repository the package resides in. 
* Covers packages from npm, PyPI, RubyGems, Composer, and Cargo.
* Locates repository from metadata collected from registry APIs. 
* Validates repository and locates sub-directory through a set of heuristics for each package ecosystem. For npm, Composer, and Cargo packages, package-locator looks at the manifest file (:code:`package.json`, :code:`composer.json`, and :code:`Cargo.toml`) to locate package specific code. For RubyGems and PyPI packages, package-locator either looks at the manifest file (:code:`gemspec` file) or compares the files present in the registry with the files present in the repository.  


Installation
------------

You can install *package-locator* via pip_ from PyPI_:

.. code:: console

   $ pip install package-locator


Usage
-----
..
    <!-- Please see the `Command-line Reference <Usage_>`_ for details. -->

:code:`from package_locator.locator import get_repository_url_and_subdir` is the primary function offered by package-locator. The function takes two inputs - ecosystem and package. The ecosystem names need to be provided as per defined within package-locator. You can import :code:`from package-locator.common import CARGO, NPM, PYPI, COMPOSER, RUBYGEMS` and then use the constant values to indicate the ecosystem name. The function returns the source code repository URL and the sub-directory within the repository where the input package resides in. For example, :code:`get_repository_url_and_subdir(NPM, "react")` call returns :code:`("https://github.com/facebook/react", "./packages/react")`.


Credits
-------

This package was created with cookietemple_ using Cookiecutter_ based on Hypermodern_Python_Cookiecutter_.

.. _cookietemple: https://cookietemple.com
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _PyPI: https://pypi.org/
.. _Hypermodern_Python_Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python
.. _pip: https://pip.pypa.io/
.. _Usage: https://package-locator.readthedocs.io/en/latest/usage.html
