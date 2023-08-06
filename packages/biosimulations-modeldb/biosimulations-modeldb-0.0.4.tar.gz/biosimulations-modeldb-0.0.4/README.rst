|Continuous integration| |Test coverage| |All Contributors|

BioSimulations-ModelDB
======================

BioSimulations-ModelDB provides a command-line application for
publishing the `ModelDB model
repository <https://senselab.med.yale.edu/ModelDB/>`__ of neural models
to the `BioSimulations <https://biosimulations.org>`__ repository for
simulation projects.

This command-line program is run weekly by the GitHub action in this
repository.

Installation
------------

Requirements
~~~~~~~~~~~~

-  Python >= 3.7
-  pip
-  XPP

Install latest revision from GitHub
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

   git clone --recurse-submodules https://github.com/biosimulations/biosimulations-modeldb
   pip install biosimulations-modeldb/

API documentation
-----------------

API documentation is available
`here <https://docs.biosimulations.org/repositories/modeldb>`__.

License
-------

This package is released under the `MIT license <LICENSE>`__.

Development team
----------------

This package was developed by the `Karr Lab <https://www.karrlab.org>`__
at the Icahn School of Medicine at Mount Sinai in New York and the
`Center for Reproducible Biomedical
Modeling <http://reproduciblebiomodels.org>`__. ModelDB was developed by
the `Sense Lab <https://senselab.med.yale.edu/>`__ at Yale University
with assistance from the contributors listed `here <CONTRIBUTORS.md>`__.

Contributing to BioSimulations-ModelDB
--------------------------------------

We enthusiastically welcome contributions to BioSimulations-ModelDB!
Please see the `guide to contributing <CONTRIBUTING.md>`__ and the
`developer's code of conduct <CODE_OF_CONDUCT.md>`__.

Acknowledgements
----------------

This work was supported by National Institutes of Health award
P41EB023912.

Questions and comments
----------------------

Please contact the `BioSimulations
Team <mailto:info@biosimulations.org>`__ with any questions or comments
about this package. Please contact the `ModelDB
Team <mailto:curator@modeldb.science>`__ with any questions or comments
about ModelDB.

.. |Continuous integration| image:: https://github.com/biosimulations/biosimulations-modeldb/actions/workflows/ci.yml/badge.svg
   :target: https://github.com/biosimulations/biosimulations-modeldb/actions/workflows/ci.yml
.. |Test coverage| image:: https://codecov.io/gh/biosimulations/biosimulations-modeldb/branch/dev/graph/badge.svg
   :target: https://codecov.io/gh/biosimulations/biosimulations-modeldb
.. |All Contributors| image:: https://img.shields.io/github/all-contributors/biosimulations/biosimulations-modeldb/HEAD
   :target: #contributors-
