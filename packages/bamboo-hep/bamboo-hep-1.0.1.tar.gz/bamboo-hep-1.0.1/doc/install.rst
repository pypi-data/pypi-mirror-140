Installation and setup
======================

Dependencies and environment
----------------------------

Bamboo_ only depends on python3 (with pip/setuptools to install PyYAML and
numpy if needed) and a recent version of ROOT (6.20/00 is the minimum
supported version, as it introduces some compatibility features for the
`new PyROOT`_ in 6.22/00).

On ingrid and lxplus (or any machine with cvmfs), an easy way to get such
a recent version of ROOT is through a CMSSW release that depends on it,
or from the `SPI LCG distribution`_, e.g.

.. code-block:: sh

   source /cvmfs/sft.cern.ch/lcg/views/LCG_100/x86_64-centos7-gcc10-opt/setup.sh
   python -m venv bamboovenv
   source bamboovenv/bin/activate

(the second command creates a `virtual environment`_
to install python packages in, after installation it is sufficient to run two
other commands, to pick up the correct base system and then the installed
packages).

Alternatively, a `conda environment`_ (e.g. with `Miniconda`_) can be created
with

.. code-block:: sh

   conda config --add channels conda-forge # if not already present
   conda create -n test_bamboo root pyyaml numpy cmake boost
   conda activate test_bamboo

and bamboo_ installed directly there with pip, or in a `virtual environment`_
inside the `conda environment`_ (make sure to pass ``--system-site-packages``
to ``venv`` then); `conda-build`_ recipes are
`in the plans <https://gitlab.cern.ch/cp3-cms/bamboo/-/issues/65>`_.

A `docker image <https://hub.docker.com/r/pieterdavid/bamboo-docker>`_
(based on `repo2docker <https://repo2docker.readthedocs.io/en/latest/>`_,
`configuration <https://github.com/pieterdavid/bamboo-docker>`_) with an
up-to-date version of bamboo_ and plotIt_ is also available.
It is compatible with `binder <https://mybinder.readthedocs.io/en/latest/>`_,
which can be used to run some
`examples <https://github.com/pieterdavid/bamboo-opendata-examples>`_ without
installing anything locally.

Some features bring in additional dependencies. Bamboo_ should detect if these
are relied on and missing, and print a clear error message in that case.
Currently, they include:

- the dasgoclient executable (and a valid grid proxy) for retrieving the list
  of files in samples specified with ``db: das:/X/Y/Z``. Due to some
  interference with the setup script above, the best is to run the cms
  environment scripts first, and also run ``voms-proxy-init`` then (this can
  alternatively also be done from a different shell on the same machine)
- the SAMADhi_ python library, to retrieve the list of files in samples
  specified with ``db: SAMADhi:<ID-or-name>`` (not yet integrated)
- the slurm command-line tools, and CP3SlurmUtils_, which can be loaded with
  ``module load slurm/slurm_utils`` on the ingrid ui machines
- the ``makePUReWeightJSON`` script can make a plot of the PU distributions
  and weights if the ``--makePlot`` option is given, but it needs matplotlib_
  for that
- machine learning libraries (libtorch_, Tensorflow-C_, lwtnn_): see
  :ref:`this section<installmachinelearning>` for more information
- writing out tables in LaTeX format from cutflow reports relies needs
  pyplotit_ (see below)

.. _installbase:

Installation
------------

Bamboo_ can (and should, in most cases) be installed in a
`virtual environment`_ or conda environment (see above) with pip,
minimally either one of

.. code-block:: sh

   pip install git+https://gitlab.cern.ch/cp3-cms/bamboo.git
   pip install git+ssh://git@gitlab.cern.ch:7999/cp3-cms/bamboo.git

but in the current development stage it may be useful to install from
a local clone, such that you can use it to test and propose changes, using

.. code-block:: sh

   git clone -o upstream https://gitlab.cern.ch/cp3-cms/bamboo.git /path/to/your/bambooclone
   pip install /path/to/your/bambooclone ## e.g. ./bamboo (not bamboo - a package with that name exists)

such that you can update later on with (inside ``/path/to/your/bambooclone``)

.. code-block:: sh

   git pull upstream master
   pip install --upgrade .


It is also possible to install bamboo in editable mode for development;
to avoid problems, this should be done in a separate virtual environment:

.. code-block:: sh

   python -m venv devvenv ## deactivate first, or use a fresh shell
   source devvenv ## deactivate first, or use a fresh shell
   pip install -e ./bamboo

Note that this will store cached build outputs in the ``_skbuild`` directory.
``python setup.py clean --all`` can be used to clean this up
(otherwise they will prevent updating the non-editabl install).

The documentation can be built locally with ``python setup.py build_sphinx``,
and for running all (or some) tests the easiest is to call ``pytest`` directly,
with the ``bamboo/tests`` directory to run all tests, or with a specific file
to check only the tests defined there.

.. note::

   bamboo is a shared package, so everything that is specific to a single
   analysis (or a few related analyses) is best stored elsewhere (e.g. in
   ``bamboodev/myanalysis`` in the example below); otherwise you will need to
   be very careful when updating to a newer version.

   The ``bambooRun`` command can pick up code in different ways, so it is
   possible to start from a single python file, and move to a pip-installed
   analysis package later on when code needs to be shared between modules.

For combining the different histograms in stacks and producing pdf or png files,
which is used in many analyses, the plotIt_ tool is used.
It can be installed with cmake, e.g.

.. code-block:: sh

   git clone -o upstream https://github.com/cp3-llbb/plotIt.git /path/to/your/plotitclone
   mkdir build-plotit
   cd build-plotit
   cmake -DCMAKE_INSTALL_PREFIX=$VIRTUAL_ENV /path/to/your/plotitclone
   make -j2 install
   cd -

where ``-DCMAKE_INSTALL_PREFIX=$VIRTUAL_ENV`` ensures that ``make install``
will put the ``plotIt`` executable directly in the ``bin`` directory of the
virtualenv (if not using a virtualenv, its path can be passed to ``bambooRun``
with the ``--plotIt`` command-line option).

plotIt_ is very efficient at what it does, but not so easy to adapt to producing
efficiently plots, overlays of differently defined distributions etc.
Therefore a python implementation of its main functionality was started in the
pyplotit_ package, which can be installed with

.. code-block:: sh

   pip install git+https://gitlab.cern.ch/cp3-cms/pyplotit.git

or editable from a local clone:

.. code-block:: sh

   git clone -o upstream https://gitlab.cern.ch/cp3-cms/pyplotit.git
   pip install -e pyplotit

pyplotit_ parses plotIt_ YAML files and implements the same grouping and
stack-building logic; an easy way to get started with it is through the
``iPlotIt`` script, which parses a plotIt_ configuration file and launches
an IPython shell.
Currently this is used in bamboo_ for producing yields tables from cutflow reports.
It is also very useful for writing custom postprocess functions, see
:ref:`this recipe<recipeotherhistogrampostprocessing>` for an example.

To use scalefactors and weights in the new CMS JSON format, the correctionlib_
package should be installed with

.. code-block:: sh

   pip install --no-binary=correctionlib correctionlib


The calculators modules for
:ref:`jet and MET corrections and systematic variations <recipejetsystematics>`
were moved to a separate repository and package, such that they can also be used
from other frameworks.
The repository can be found at
`cp3-cms/CMSJMECalculators <https://gitlab.cern.ch/cp3-cms/CMSJMECalculators.git>`_,
and installed with

.. code-block:: sh

   pip install git+https://gitlab.cern.ch/cp3-cms/CMSJMECalculators.git


For the impatient: recipes for installing and updating
''''''''''''''''''''''''''''''''''''''''''''''''''''''

Putting the above commands together, the following should give you a virtual
environment with bamboo_, and a clone of bamboo_ and plotIt in case you need to
modify them, all under ``bamboodev``:

Fresh install
#############

.. code-block:: sh

   mkdir bamboodev
   cd bamboodev
   # make a virtualenv
   source /cvmfs/sft.cern.ch/lcg/views/LCG_100/x86_64-centos7-gcc10-opt/setup.sh
   python -m venv bamboovenv
   source bamboovenv/bin/activate
   # clone and install bamboo
   git clone -o upstream https://gitlab.cern.ch/cp3-cms/bamboo.git
   pip install ./bamboo
   # clone and install plotIt
   git clone -o upstream https://github.com/cp3-llbb/plotIt.git
   mkdir build-plotit
   cd build-plotit
   cmake -DCMAKE_INSTALL_PREFIX=$VIRTUAL_ENV ../plotIt
   make -j2 install
   cd -

Environment setup
#################

Once bamboo_ and plotIt have been installed as above, only the following two
commands are needed to set up the environment in a new shell:

.. code-block:: sh

   source /cvmfs/sft.cern.ch/lcg/views/LCG_100/x86_64-centos7-gcc10-opt/setup.sh
   source bamboodev/bamboovenv/bin/activate

Update bamboo
#############

Assuming the environment is set up as above; this can also be used to test a
pull request or local modifications to the bamboo_ source code

.. code-block:: sh

   cd bamboodev/bamboo
   git checkout master
   git pull upstream master
   pip install --upgrade .

Update plotIt
#############

Assuming the environment is set up as above; this can also be used to test a
pull request or local modifications to the plotIt source code.
If a plotIt build directory already exists it should have been created with the same
environment, otherwise the safest solution is to remove it.

.. code-block:: sh

   cd bamboodev
   mkdir build-plotIt
   cd build-plotit
   cmake -DCMAKE_INSTALL_PREFIX=$VIRTUAL_ENV ../plotIt
   make -j2 install
   cd -

Move to a new LCG release or install an independent version
############################################################

Different virtual environments can exist alongside each other, as long as for
each the corresponding base LCG distribution is setup in a fresh shell.
This allows to have e.g. one stable version used for analysis, and another one
to test experimental changes, or check a new LCG release, without touching a
known working version.

.. code-block:: sh

   cd bamboodev
   source /cvmfs/sft.cern.ch/lcg/views/LCG_100/x86_64-centos7-gcc10-opt/setup.sh
   python -m venv bamboovenv_X
   source bamboovenv_X/bin/activate
   pip install ./bamboo
   # install plotIt (as in "Update plotIt" above)
   mkdir build-plotit
   cd build-plotit
   cmake -DCMAKE_INSTALL_PREFIX=$VIRTUAL_ENV ../plotIt
   make -j2 install
   cd -

Test your setup
---------------

Now you can run a few simple tests on a CMS NanoAOD to see if the installation
was successful. A minimal example is run by the following command:

.. code-block:: sh

   bambooRun -m /path/to/your/bambooclone/examples/nanozmumu.py:NanoZMuMu /path/to/your/bambooclone/examples/test1.yml -o test1

which will run over a single sample of ten events and fill some histograms
(in fact, only one event passes the selection, so they will not look very
interesting).
If you have a NanoAOD file with muon triggers around, you can put its path
instead of the test file in the yml file and rerun to get a nicer plot (xrootd
also works, but only for this kind of tests |---| in any practical case the
performance benefit of having the files locally is worth the cost of replicating
them).

Getting started
---------------

The test command above shows how bamboo is typically run: using the
:ref:`bambooRun<ugbambooRun>` command, with a python module that specifies what
to run, and an :ref:`analysis YAML file<uganalysisyaml>` that specifies which
samples to process, and how to combine them in plots (there are several options
to run a small test, or submit jobs to the batch system when processing a lot
of samples).

A more realistic analysis YAML configuration file is
`bamboo/examples/analysis_zmm.yml <https://gitlab.cern.ch/cp3-cms/bamboo/blob/master/examples/analysis_zmm.yml>`_,
which runs on a significant fraction of the 2016 and 2017 ``DoubleMuon`` data
and the corresponding Drell-Yan simulated samples.
Since the samples are specified by their DAS path in this case, the
``dasgoclient`` executable and a valid grid proxy are needed for resolving
those to files, and a :ref:`configuration file<ugenvconfig>` that describes the
local computing environment (i.e. the root path of the local CMS grid storage,
or the name of the redirector in case of using xrootd); examples are included
for the UCLouvain-CP3 and CERN (lxplus/lxbatch) cases.

The corresponding
`python module <https://gitlab.cern.ch/cp3-cms/bamboo/blob/master/examples/nanozmumu.py>`_
shows the typical structure of ever tighter event selections that derive from
the base selection, which accepts all the events in the input, and plots that
are defined based on these selection, and returned in a list from the main
method (this corresponds to the pdf or png files that will be produced).

The module deals with a decorated version of the tree, which can also be
inspected from an IPython shell by using the ``-i`` option to ``bambooRun``,
e.g.

.. code-block:: sh

   bambooRun -i -m /path/to/your/bambooclone/examples/nanozmumu.py:NanoZMuMu /path/to/your/bambooclone/examples/test1.yml

together with the helper methods defined on :doc:`this page<treefunctions>`,
this allows to define a wide variety of selection requirements and variables.

The :doc:`user guide<userguide>` contains a much more detailed description of
the different files and how they are used, and the
:doc:`analysis recipes page<recipes>` provides more information about the
bundled helper methods for common tasks.
The :doc:`API reference<apiref>` describes all available user-facing methods
and classes.
If the builtin functionality is not sufficient, some hints on extending or
modifying bamboo can be found in the :doc:`advanced topics<advanced>` and the
:doc:`hacking guide<hacking>`.

.. _installmachinelearning:

Machine learning packages
-------------------------

In order to evaluate machine learning classifiers, bamboo_ needs to find the
necessary C(++) libraries, both when the extension libraries are compiled and
at runtime (so they need to be installed before (re)installing bamboo_).
libtorch_ is searched for in the ``torch`` package with ``pkg_resources``,
which unfortunately does not always work due to ``pip`` build isolation.
This can be bypassed by passing ``--no-isolated-build`` when installing, or by
installing ``bamboo[torch]``, which will install it as a dependency (it is
quite big, so if the former method works it should be preferred).
The ``--no-isolated-build`` option is a workaround: when passing CMake options
to pip install (see
`scikit-build#479 <https://github.com/scikit-build/scikit-build/issues/479>`_)
will be possible, that will be a better solution.
The minimum version required for  libtorch_ is 1.5 (due to changes in
the C++ API), which is available from LCG_99 on (contains libtorch_ 1.7.0).
Tensorflow-C_ and lwtnn_ will be searched for (by cmake and the dynamic library
loader) in the default locations, supplemented with the currently active
`virtual environment`_, if any (scripts to install them there directly are
included in the bamboo source code respository, as
``ext/install_tensorflow-c.sh`` and ``ext/install_lwtnn.sh``).
`ONNX Runtime`_ is not part of the LCG distribution, and will be searched for
in the standard locations.
It can be added to the `virtual environment`_ by following the
`instruction <https://github.com/microsoft/onnxruntime/blob/master/BUILD.md#linuxmacos>`_
to build from source, with the additional option
``--cmake_extra_defines=CMAKE_INSTALL_PREFIX=$VIRTUAL_ENV``, after which
``make install`` from its ``build/Linux/<config>`` will install it correctly
(replacing ``<config>`` by the CMake build type, e.g. Release or
RelWithDebInfo).

.. note:: Installing a newer version of libtorch_ in a virtualenv if it is
   also available through the ``PYTHONPATH`` (e.g. in the LCG distribution)
   generally does not work, since virtualenv uses ``PYTHONHOME``, which has
   lower precedence.
   For the pure C(++) libraries Tensorflow-C_ and lwtnn_ this could be made to
   work, but currently the virtual environment is only explicitly searched if
   they are not found otherwise.
   Therefore it is recommended to stick with the version provided by the LCG
   distribution, or set up an isolated environment with conda |---| see the
   issues `#68`_ (for now) and `#65`_ for more information. When a stable
   solution is found it will be added here.

.. warning:: the libtorch_ and Tensorflow-C_ builds in LCG_98python3 contain
   AVX2 instructions (so one of
   `these <https://en.wikipedia.org/wiki/Advanced_Vector_Extensions#CPUs_with_AVX2>`_
   CPU generations).
   See issue `#68`_ for more a more detailed discussion, and a possible workaround.

.. _nocvmfsinstallCP3:

EasyBuild-based installation at CP3
-----------------------------------

On the ingrid/manneback cluster at UCLouvain-CP3, and other environments that
use EasyBuild_, it is also possible to install bamboo_ based on the dependencies
that are provided through this mechanism (potentially with some of them built
as user modules).
The LCG source script in the instructions above should then be replaced by e.g.

.. code-block:: sh

   module load ROOT/6.22.08-foss-2019b-Python-3.7.4 CMake/3.15.3-GCCcore-8.3.0 \
      Boost/1.71.0-gompi-2019b matplotlib/3.1.1-foss-2019b-Python-3.7.4 \
      PyYAML/5.1.2-GCCcore-8.3.0 TensorFlow/2.1.0-foss-2019b-Python-3.7.4


.. _bamboo: https://cp3.irmp.ucl.ac.be/~pdavid/bamboo/index.html

.. _CP3SlurmUtils: https://cp3-git.irmp.ucl.ac.be/cp3-support/helpdesk/wikis/Slurm#the-cp3slurmutils-package

.. _matplotlib: https://matplotlib.org

.. _SAMADhi: https://cp3.irmp.ucl.ac.be/samadhi/index.php

.. _virtual environment: https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments

.. _plotIt: https://github.com/cp3-llbb/plotIt

.. _libtorch: https://pytorch.org/cppdocs/

.. _Tensorflow-C: https://www.tensorflow.org/install/lang_c

.. _lwtnn: https://github.com/lwtnn/lwtnn

.. _ONNX Runtime: https://www.onnxruntime.ai

.. _#68: https://gitlab.cern.ch/cp3-cms/bamboo/-/issues/68

.. _#65: https://gitlab.cern.ch/cp3-cms/bamboo/-/issues/65

.. _new PyROOT: https://root.cern/blog/new-pyroot-622/

.. _SPI LCG distribution: http://spi.web.cern.ch

.. _conda environment: https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#managing-envs

.. _Miniconda: https://docs.conda.io/en/latest/miniconda.html

.. _conda-build: https://docs.conda.io/projects/conda-build/en/latest/

.. _EasyBuild: https://easybuild.io

.. _pyplotit: https://gitlab.cern.ch/cp3-cms/pyplotit

.. _correctionlib: https://github.com/cms-nanoAOD/correctionlib

.. |---| unicode:: U+2014
   :trim:
