Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_ and this project adheres to
`Semantic Versioning`_.

`Unreleased`_
-------------

`2.1.1`_ - 2021-03-05
---------------------

Changed
~~~~~~~

- Do not fail scrape if some node is unresponsive (#63)

`2.1.0`_ - 2021-02-19
---------------------

Added
~~~~~

- Add command line flags to enable/disable individual collectors (#62)

Changed
~~~~~~~

- Update docker base image

`2.0.3`_ - 2020-12-17
---------------------

Changed
~~~~~~~

- Fix version number

`2.0.2`_ - 2020-12-17
---------------------

Changed
~~~~~~~

- Update docker base image
- Remove dead code (#52)

`2.0.1`_ - 2020-10-21
---------------------

Changed
~~~~~~~

- Update docker image to alpine 3.12.1 (#50)
- Complete Python 3 transition (#49)
- Fix packaging (#48)

`2.0.0`_ - 2020-10-19
---------------------

Added
~~~~~

- Add `pve_storage_shared` metric (#44)

Removed
~~~~~~~

- Remove `ip` and `local` labels from `pve_node_info` gauge (#41)
- Dropped support for Python 2

`1.3.2`_ - 2020-07-02
---------------------

Changed
~~~~~~~

- Fix pypi autopublishing

`1.3.1`_ - 2020-07-02
---------------------

Changed
~~~~~~~

- Fix pypi / dockerhub autopublishing (#40)

`1.3.0`_ - 2020-07-02
---------------------

Added
~~~~~

- Autopublish to pypi (#39)
- Add dockerfile and autopublish to dockerhub (#38)
- Move repo to prometheus-pve github org (#36, #37)


`1.2.2`_ - 2020-05-18
---------------------

Changed
~~~~~~~

- Fix failure when some node is unavailable (#31)

`1.2.1`_ - 2020-05-03
---------------------

Changed
~~~~~~~

-  Refuse to start with invalid configuration (#29)
-  Log exceptions thrown during view rendering (#28)

`1.2.0`_ - 2020-04-20
---------------------

Added
~~~~~

-  Add pve_onboot_status read from vm/container config (#22)

`1.1.2`_ - 2018-10-17
---------------------

Changed
~~~~~~~

-  Fixed issues with VM names when PVE is down. (#14, #15)

`1.1.1`_ - 2018-02-28
---------------------

Changed
~~~~~~~

-  Fix for target/module URL parameters being ignored, fixes #9 and #11


`1.1.0`_ - 2018-01-22
---------------------

Added
~~~~~

-  IPv6 support


.. _Keep a Changelog: http://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: http://semver.org/spec/v2.0.0.html
.. _Unreleased: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.1.1...HEAD
.. _2.1.1: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.1.0...v2.1.1
.. _2.1.0: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.0.3...v2.1.0
.. _2.0.3: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.0.2...v2.0.3
.. _2.0.2: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.0.1...v2.0.2
.. _2.0.1: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.0.0...v2.0.1
.. _2.0.0: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v1.3.2...v2.0.0
.. _1.3.2: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v1.3.1...v1.3.2
.. _1.3.1: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v1.3.0...v1.3.1
.. _1.3.0: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v1.2.2...v1.3.0
.. _1.2.2: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v1.2.1...v1.2.2
.. _1.2.1: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v1.2.0...v1.2.1
.. _1.2.0: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v1.1.2...v1.2.0
.. _1.1.2: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v1.1.1...v1.1.2
.. _1.1.1: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v1.1.0...v1.1.1
.. _1.1.0: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v1.0.0...v1.1.0
