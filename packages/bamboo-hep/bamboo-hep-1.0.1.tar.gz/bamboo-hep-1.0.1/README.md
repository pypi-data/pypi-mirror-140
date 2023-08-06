# Bamboo: A high-level HEP analysis library for ROOT::RDataFrame

[![Documentation Status](https://readthedocs.org/projects/bamboo-hep/badge/?version=latest)](https://bamboo-hep.readthedocs.io/en/latest/?badge=latest)

The [`ROOT::RDataFrame`](https://root.cern.ch/doc/master/classROOT_1_1RDataFrame.html)
class provides an efficient and flexible way to process per-event information
(stored in a `TTree`) and e.g. aggregate it into histograms.

With the typical pattern of storing object arrays as a structure of arrays
(variable-sized branches with a common prefix in the names and length),
the expressions that are typically needed for a complete analysis quickly become
cumbersome to write (with indices to match, repeated sub-expressions etc.).

As an example, imagine the expression needed to calculate the invariant mass
of the two leading muons from a CMS NanoAOD file (which stores 4-momenta with
pt, eta and phi branches): one way is to construct LorentzVector objects,
sum and evaluate the invariant mass.
Next imagine doing the same thing with the two highest-pt jets that have a b-tag
and are not within some cone of the two leptons you already selected in another
way (while keeping the code maintainable enough to allow for passing jet momenta
with a systematic variation applied).

Bamboo attempts to solve this problem by automatically constructing
lightweight python wrappers based on the structure of the `TTree`,
which allow to construct such expression with high-level code, similar to the
language that is commonly used to discuss and describe them. By constructing
an object representation of the expression, a few powerful operations can be
used to compose complex expressions.
This also allows to automate the construction of derived expressions, e.g. for
shape systematic variation histograms.

Building selections, plots etc. with such expressions is analysis-specific, but
the mechanics of loading data samples, processing them locally or on a batch
system, combining the outputs for different samples in an overview etc.
is very similar over a broad range of use cases.
Therefore a common implementation of these is provided, such that the analyst
only needs to provide a subclass with their selection and plot definitions,
and a configuration file with a list of samples, and instructions how to
display them.

## Documentation

The HTML documentation (with a longer introduction, installation instructions,
recipes for common tasks and an API reference of the classes and methods) is
available [here](https://bamboo-hep.readthedocs.io/).

## Development

Bamboo has been in development since early 2019, and is actively used by
several analyses.
The experience from daily use, and the addition of new features in the
underlying ROOT::RDataFrame package, ideas for improvements and further
development continue to pop up.
Please have a look at the
[guidelines](https://gitlab.cern.ch/cp3-cms/bamboo/-/blob/master/CONTRIBUTING.md)
to also start contributing.
