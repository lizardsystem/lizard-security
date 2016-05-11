Changelog of lizard-security
===================================================


0.8 (unreleased)
----------------

- Added Jenkinsfile for automatic testing on the new
  https://jenkins.lizard.net

- Removed travis.yml file for https://travis-ci.org


0.7 (2014-08-05)
----------------

- Made changes for Django 1.6.5 compatibility. 1.4 - 1.6.5 supported
  now.


0.6 (2013-09-02)
----------------

- Add `'use_for_related_fields = True``. This secures lookups
  via ForeignKey.

- Added automatic testing with `travis CI
  <https://travis-ci.org/lizardsystem/lizard-security/>`_.


0.5 (2012-04-05)
----------------

- Added example usage in README.rst.

- Fix bug where object permissions weren't checked correctly


0.4 (2011-12-22)
----------------

- Added FilteredGeoObject manager.

- Added spatialite db for tests.


0.3 (2011-12-05)
----------------

- Added south dependency.

- Removed traces of lizard_ui which is no dependency.


0.2 (2011-12-05)
----------------

- Added missing translations.


0.1 (2011-12-05)
----------------

- 100% test coverage.

- Added a whole lot of documentation.

- Added models, object manager, admin, authentication backend and middleware.

- Added definition of terms to the README.

- Initial library skeleton created by nensskel.
