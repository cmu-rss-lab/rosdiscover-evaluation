Claims of the Artifact
======================

We believe that this artifact should be awarded both (a) Open Research Object (ORO) and (b) Research Object Reviewed (ROR) -- Reusable badges.
To qualify for either badge, artifacts must be functional, and so we first make a case that our artifact is functional before describing how it satisfies the criteria of the ORO and ROR badges.


Functional
----------

The `ICSA artifact evaluation track website <https://www.acm.org/publications/policies/artifact-review-and-badging-current>`_ deems an artifact to be Functional if it satisfies the criteria below:

::

  In order to obtain any badge every artifact will be required to be Functional, that is, it must be properly documented,
  consistent, complete, exercisable, and include appropriate evidence of verification and validation.

Where the definitions of documented, consistent, complete, and exercisable come from the **Artifacts Evaluated -- Functional v1.1** criteria laid out in the `ACM policy on Artifact Review and Badging Version 1.1 <https://www.acm.org/publications/policies/artifact-review-and-badging-current>`_:

::

  * Documented: At minimum, an inventory of artifacts is included, and sufficient description provided to enable the
    artifacts to be exercised.

  * Consistent: The artifacts are relevant to the associated paper, and contribute in some inherent way to the
    generation of its main results.

  * Complete: To the extent possible, all components relevant to the paper in question are included.
    (Proprietary artifacts need not be included. If they are required to exercise the package then this should be
    documented, along with instructions on how to obtain them. Proxies for proprietary data should be included so as to
    demonstrate the analysis.)

  * Exercisable: Included scripts and/or software used to generate the results in the associated paper can be
    successfully executed, and included data can be accessed and appropriately manipulated.


Below, we argue how this artifact satifies each of the above criteria:

* **Documented:** An outline of the replication package and a detailed description of its contents are provided in README.rst.
  Installation instructions for the artifact are given in INSTALL.rst, and steps for reproducing the results of the paper are given in README.rst.
* **Consistent:** The artifacts provided in this replication package include the source code and executables for ROSDiscover toolchain (i.e., an implementation of the technique presented in the paper), prebuilt images for the evaluation dataset (as well as their sources), the infrastructure used to run all of the experiments in the paper, and the raw and processed results themselves.
* **Complete:** See above. All of the necessary software, data, and instructions for reproducing the results of the paper are included in this replication package.
* **Exercisable:** We provide a Docker-based setup for reliably reproducing the results of the experiments reported in the paper, complete with instructions for installing and running that setup.


Open Research Object (ORO)
--------------------------

The `NISO Recommended Practice on Reproducibility Badging and Definitions <https://www.niso.org/standards-committees/reproducibility-badging>`_ give the following description of the ORO badge:

::

  This badge signals that author-created digital objects used in the research (including data and code)
  are permanently archived in a public repository that assigns a global identifier and guarantees
  persistence, and are made available via standard open licenses that maximize artifact availability.


Similarly, the `ICSA artifact evaluation track website <https://icsa-conferences.org/2022/conference-tracks/artifact-evaluation-track>`_ describes artifacts with the ORO badge as being:

::

  Functional + placed on a publicly accessible archival repository.
  A DOI or link to this repository along with a unique identifier for the object is provided (this matches the ACM “Available” badge).

This replication package is hosted on `Zenodo <https://zenodo.org>`_, a long-term archival service that `will exist as long as its host, the CERN laboratory, which will has an experiment programme defined for at least the next 20 years <https://about.zenodo.org/policies>`_. The replication package can be accessed via the following DOI: https://doi.org/10.5281/zenodo.5834633.


Research Object Reviewed (ROR) -- Reusable
------------------------------------------

The ICSA artifact evaluation track gives the following criteria for this badge:

::

  Functional + very carefully documented and well-structured to the extent that reuse and repurposing is facilitated.
  In particular, norms and standards of the research community for artifacts of this type are strictly adhered to.


This replication package contains components that are designed for reuse and repurposing:

* **ROSDiscover (https://github.com/rosqual/rosdiscover):** provides an implementation of the technique described in the paper.
  It is designed to, among other purposes, recover run-time architectures from ROS applications, provided in the form of a Docker image and an accompanying configuration file.
  Further instructions on the general use of ROSDiscover can be found in its README file, available either in its archival form in the :code:`deps/rosdiscover` directory of this artifact, or, preferably, in its up-to-date form on GitHub at:https://github.com/rosqual/rosdiscover.
* **ROSWire (https://github.com/rosqual/roswire):**
* **Our experiment infrastructure:**
* **Our evaluation dataset:**

TODO: Make argument that we go far above and beyond the expectations of typical research artifacts.
We follow appropriate software engineering norms and best practices (e.g., those related to Docker and Python).
