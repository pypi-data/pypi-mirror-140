Thank you for using or evaluating bamboo, and considering to contribute back!

These guidelines give an overview of how we organise the development.
This is an open-source project for a reason: any (prospective) user is kindly invited
to provide feedback and help improve the code and documentation.

The following communication channels are available:
- the bamboo channel on the [CP3](https://cp3-mm.irmp.ucl.ac.be/cp3-llbb/channels/bamboo)
  and [CERN/CMS](https://mattermost.web.cern.ch/cms-exp/channels/bamboo) mattermost instances,
  for any questions about using the package, adapting it to your needs, or the development
- [GitLab issues](https://gitlab.cern.ch/cp3-cms/bamboo/-/issues) to report anything that
  is not working as expected, or should be added (including in the documentation);
  if you are not sure, the safe option is to ask on mattermost first
  (your question is likely to get noticed faster and by more people,
  and the platform is more suitable for discussions with a shorter turnaround time)
- [GitLab merge requests](https://gitlab.cern.ch/cp3-cms/bamboo/-/merge_requests)
  if you want to propose a change or fix a bug, and have (some of) the code ready
Please check if there is already an existing issue (or open merge request)
that answers your question before opening a new one.

The code is designed such that most customization can be done from the analysis code,
without modifying the framework; this is also a great way to develop new features,
but please consider proposing them for inclusion in the bamboo package if others
may also benefit.
Generally, any additions or changes that can be useful for using bamboo are welcome,
provided that their benefit is worth the development and review effort,
and justifies the impact on existing use cases
(e.g. a small helper function is very likely to be accepted,
if it is sound and not confusing to use, while changing an API
that all existing analysis methods rely on should be avoided if possible).
Please get in contact early, we are happy to discuss to avoid misunderstandings.

The ['Under the hood'](https://bamboo-hep.readthedocs.io/en/latest/hacking.html)
page of the documentation collects useful information for development,
such as how to debug problems, use the tests, and understand the design
of the internals.
