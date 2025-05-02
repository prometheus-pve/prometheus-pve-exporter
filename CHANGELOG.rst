Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_ and this project adheres to
`Semantic Versioning`_.

`Unreleased`_
-------------

`3.5.4`_ - 2025-05-02
---------------------

Changed
~~~~~~~

- Fix GHA workflow failing on artifact attestation (#330)


`3.5.3`_ - 2025-04-17
---------------------

Changed
~~~~~~~

- Fix storage content label causing churn rate + cardinality explosion (#326)
- Add ghcr.io as registry (#325)


`3.5.2`_ - 2025-02-18
---------------------

Changed
~~~~~~~

- Bump alpine from 3.21.2 to 3.21.3 (#321)
- Bump cryptography from 43.0.1 to 44.0.1 (#319)
- Bump paramiko from 3.5.0 to 3.5.1 (#318)


`3.5.1`_ - 2025-01-20
---------------------

Changed
~~~~~~~

- Bump alpine from 3.21.0 to 3.21.2 (#315)


`3.5.0`_ - 2025-01-02
---------------------

Added
~~~~~

- Extend storage info (#312)
- Add pve_ha_state and pve_lock_state metrics (#311)


`3.4.7`_ - 2024-12-17
---------------------

Changed
~~~~~~~

- Bump proxmoxer from 2.1.0 to 2.2.0 (#309)
- Bump prometheus-client from 0.21.0 to 0.21.1 (#308)
- Bump alpine from 3.20.3 to 3.21.0 (#307)


`3.4.6`_ - 2024-12-02
---------------------

Changed
~~~~~~~

- Fix metrics docs (#301)
- Bump werkzeug from 3.0.4 to 3.1.3 (#297)
- Bump prometheus-client from 0.20.0 to 0.21.0 (#286)


`3.4.5`_ - 2024-09-16
---------------------

Changed
~~~~~~~

- Bump cryptography to 43.0.1 (#283)
- Bump paramiko from 3.4.1 to 3.5.0 (#282)
- Bump alpine from 3.20.2 to 3.20.3 (#281)
- Bump werkzeug from 3.0.3 to 3.0.4 (#277)


`3.4.4`_ - 2024-08-15
---------------------

Changed
~~~~~~~

- Bump pyyaml from 6.0.1 to 6.0.2 (#274)
- Bump proxmoxer from 2.0.1 to 2.1.0 (#273)
- Bump paramiko from 3.4.0 to 3.4.1 (#272)
- Bump gunicorn from 22.0.0 to 23.0.0 (#271)
- Bump alpine from 3.20.1 to 3.20.2 (#269)
- Bump certifi from 2023.11.17 to 2024.7.4 (#263)


`3.4.3`_ - 2024-07-03
---------------------

Changed
~~~~~~~

- Bump alpine from 3.19.1 to 3.20.1 (#260)
- Bump urllib3 from 2.1.0 to 2.2.2 (#259)
- Bump requests from 2.32.0 to 2.32.3 (#256)
- Bump docker/build-push-action from 5 to 6 (#258)


`3.4.2`_ - 2024-05-26
---------------------

Changed
~~~~~~~

- Bump requests from 2.31.0 to 2.32.0 (#251)


`3.4.1`_ - 2024-05-06
---------------------

Changed
~~~~~~~

- Bump werkzeug from 3.0.2 to 3.0.3 (#249)


`3.4.0`_ - 2024-04-30
---------------------

Added
~~~~~

- Add tags label to pve_guest_info metric (#246)


`3.3.0`_ - 2024-04-27
---------------------

Added
~~~~~

- Add ZFS replication metrics (#243)


`3.2.5`_ - 2024-04-17
---------------------

Changed
~~~~~~~

- Bump gunicorn from 21.2.0 to 22.0.0 (#241)


`3.2.4`_ - 2024-04-12
---------------------

Changed
~~~~~~~

- Bump idna from 3.6 to 3.7 (#239)
- Bump werkzeug from 3.0.1 to 3.0.2 (#237)


`3.2.3`_ - 2024-02-25
---------------------

Changed
~~~~~~~

- Bump cryptography from 42.0.2 to 42.0.4 (#232)


`3.2.2`_ - 2024-02-06
---------------------

Changed
~~~~~~~

- Bump cryptography from 41.0.7 to 42.0.0 (#226)
- Bump alpine container image version from 3.19.0 to 3.19.1 (#225)


`3.2.1`_ - 2024-01-07
---------------------

Changed
~~~~~~~

- Build cffi and pyyaml from source (#222)
- Use appropriate build tools to create dist for pypi (#220)


`3.2.0`_ - 2024-01-06
---------------------

Changed
~~~~~~~

- Bump alpine from 3.18.5 to 3.19.0 (#216)
- Update to pylint 3 (#218)
- Use pyproject.toml, pip-compile and venv to build container image (#215)


`3.1.0`_ - 2024-01-03
---------------------

Added
~~~~~

- Adding template label to pve_guest_info metric (#208)

Changed
~~~~~~~

- Simplify container build spec (#210)
- Fix coding style after template label addition (#209)
- Bump actions/download-artifact from 3 to 4 (#205)
- Bump actions/upload-artifact from 3 to 4 (#206)
- Correct cluster and node params (#202)
- Extract cluster and node collectors into separate files (#198)


`3.0.2`_ - 2023-11-05
---------------------

Changed
~~~~~~~

- Specify same arguments for upload-artifact and download-artifact actions
  (#196)


`3.0.1`_ - 2023-11-05
---------------------

Changed
~~~~~~~

- Revert to deprecated way of building packages (#193)


`3.0.0`_ - 2023-11-05
---------------------

Changed (BREAKING)
~~~~~~~~~~~~~~~~~~
- Use flags instead of positional arguments for config file and listen address
  (#190)
- Scrape /nodes endpoint from current node only (#180)
- Remove tini from docker image (#179)
- Bump required python version to 3.9 (bullseye) (#162)
- Run with a dedicated user in container by default (#182)

Changed
~~~~~~~

- Implement pypi trusted publishing workflow (#187)
- Use PEP440 pattern when converting repo release tags into docker image tags (#183)
- Remove references to develop branch (#181)
- Update docker image to alpine 3.18.4 (#170)
- Bump required python version to 3.9 (in README) (#169)
- Remove fallback for BooleanOptionalAction (obsolete in python>=3.9) (#163)
- Fix github actions (#161)
- Bump actions/checkout from 2 to 4 (#177)
- ci: add dependabot (#176)
- ci: add arm64 image build (#175)


`3.0.0b1`_ - 2023-10-16
-----------------------

Changed (BREAKING)
~~~~~~~~~~~~~~~~~~
- Scrape /nodes endpoint from current node only (#180)
- Remove tini from docker image (#179)
- Bump required python version to 3.9 (bullseye) (#162)
- Run with a dedicated user in container by default (#182)

Changed
~~~~~~~
- Use PEP440 pattern when converting repo release tags into docker image tags (#183)
- Update docker image to alpine 3.18.4 (#170)
- Remove fallback for BooleanOptionalAction (obsolete in python>=3.9) (#163)
- Fix github actions (#161)
- Bump actions/checkout from 2 to 4 (#177)

Added
~~~~~
- ci: add dependabot (#176)
- ci: add arm64 image build (#175)


`2.3.1`_ - 2023-08-02
---------------------

Changed
~~~~~~~
- Update docker image to alpine 3.18.2 (#158)


`2.3.0`_ - 2023-04-26
---------------------

Added
~~~~~
- Use gunicorn instead of the Werkzeug development server (#132)
- Add package __main__.py as an additional cli entrypoint (#138)

Changed
~~~~~~~
- Update container image to proxmoxer 2.0.1 (#144)
- Update docker image to alpine 3.17.3 (#140)
- README: Fix Grafana dashboard URL (#128)
- Update README.rst (#125)


`2.2.4`_ - 2022-10-16
---------------------

Changed
~~~~~~~

- Update container image to proxmoxer 1.3.1 (#122)
- Update docker image to alpine 3.16.2 (#121)
- Update docs with metrics sample and instructions for token id (#114)


`2.2.3`_ - 2022-03-06
---------------------

Changed
~~~~~~~

- Update docker image to alpine 3.15.0 (#106)
- Update container image to proxmoxer 1.2.0 (#105)


`2.2.2`_ - 2021-09-16
---------------------

Changed
~~~~~~~

- Push image to dockerhub (#89)

`2.2.1`_ - 2021-09-16
---------------------

Changed
~~~~~~~

- Publish releases to dockerhub via gh actions (#88)
- Remove deprecated `test_suite` key from setup.py (#86)
- Update docker image to alpine 3.13.6 (#83)


`2.2.0`_ - 2021-08-27
---------------------

Added
~~~~~

- Optionally pass configuration via environment variables (#78)
- Add verfify_ssl example to readme (#76)

Changed
~~~~~~~

- Update docker image to alpine 3.13.5 (#71)

`2.1.2`_ - 2021-04-04
---------------------

Changed
~~~~~~~

- Migrate from travis to github actions (#68)
  Also switch to dockerhub automated builds
- Update docker image to alpine 3.13.4 (#67)
- Update docker image to alpine 3.13.3 (#65)

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
.. _Unreleased: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.5.4...HEAD
.. _3.5.4: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.5.3...v3.5.4
.. _3.5.3: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.5.2...v3.5.3
.. _3.5.2: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.5.1...v3.5.2
.. _3.5.1: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.5.0...v3.5.1
.. _3.5.0: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.4.7...v3.5.0
.. _3.4.7: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.4.6...v3.4.7
.. _3.4.6: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.4.5...v3.4.6
.. _3.4.5: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.4.4...v3.4.5
.. _3.4.4: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.4.3...v3.4.4
.. _3.4.3: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.4.2...v3.4.3
.. _3.4.2: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.4.1...v3.4.2
.. _3.4.1: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.4.0...v3.4.1
.. _3.4.0: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.3.0...v3.4.0
.. _3.3.0: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.2.5...v3.3.0
.. _3.2.5: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.2.4...v3.2.5
.. _3.2.4: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.2.3...v3.2.4
.. _3.2.3: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.2.2...v3.2.3
.. _3.2.2: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.2.1...v3.2.2
.. _3.2.1: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.2.0...v3.2.1
.. _3.2.0: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.1.0...v3.2.0
.. _3.1.0: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.0.2...v3.1.0
.. _3.0.2: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.0.1...v3.0.2
.. _3.0.1: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.0.0...v3.0.1
.. _3.0.0: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v3.0.0b1...v3.0.0
.. _3.0.0b1: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.3.1...v3.0.0b1
.. _2.3.1: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.3.0...v2.3.1
.. _2.3.0: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.2.4...v2.3.0
.. _2.2.3: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.2.3...v2.2.4
.. _2.2.3: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.2.2...v2.2.3
.. _2.2.2: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.2.1...v2.2.2
.. _2.2.1: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.2.0...v2.2.1
.. _2.2.0: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.1.2...v2.2.0
.. _2.1.2: https://github.com/prometheus-pve/prometheus-pve-exporter/compare/v2.1.1...v2.1.2
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
