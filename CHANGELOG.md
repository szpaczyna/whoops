# Changelog

## [1.3.0](https://github.com/szpaczyna/whoops/compare/v1.2.2...v1.3.0) (2026-11-01)


### Features

* updated grafana dasbhoards ([c07d376](https://github.com/szpaczyna/whoops/commit/c07d37678118cd32825558304799b06091a8ba40))


### Bug Fixes

* disable docker build on push to main ([4e80d7d](https://github.com/szpaczyna/whoops/commit/4e80d7d3e57f8d2cf1b0b9f52649b1a0f7035151))


### Miscellaneous

* upgrade setup python to v7 ([d152d12](https://github.com/szpaczyna/whoops/commit/d152d1205d1987cc35915f5695e923249bb7ebea))

## [1.2.2](https://github.com/szpaczyna/whoops/compare/v1.2.1...v1.2.2) (2026-10-31)


### Bug Fixes

* simplify release edit note in release workflow ([3b7de61](https://github.com/szpaczyna/whoops/commit/3b7de61c4b15c1796747c5b9d3337f766023e157))


### CI/CD

* build versioned image in release workflow ([2f53449](https://github.com/szpaczyna/whoops/commit/2f53449060761ca09a6270313f2464282b6b8f6c))
* update actions, build-only on main, add linting ([#7](https://github.com/szpaczyna/whoops/issues/7)) ([0972574](https://github.com/szpaczyna/whoops/commit/0972574fa4c324ea0e96c5f34e5b2430691626d6))

## [1.2.1](https://github.com/szpaczyna/whoops/compare/v1.2.0...v1.2.1) (2026-10-31)


### Bug Fixes

* register WhoopToken model before create_all ([f6dbd5f](https://github.com/szpaczyna/whoops/commit/f6dbd5f378a5379f24680f391f499dcb72c010d2))
* remove stray EOF from workflow file ([4c10567](https://github.com/szpaczyna/whoops/commit/4c10567e33ea3da0a1c5a2258cc4831d2ce14529))
* simplify release edit note to single line ([8eb1eb4](https://github.com/szpaczyna/whoops/commit/8eb1eb4b24aa46ba933f154ffbf3ac965cd173db))


### CI/CD

* automate semver releases and Docker image builds ([6e20c8f](https://github.com/szpaczyna/whoops/commit/6e20c8ff5a3d8c01dcf6e0089628a1df78e4cb3c))
* automate semver releases and Docker image builds ([8c750ca](https://github.com/szpaczyna/whoops/commit/8c750ca756ed2c8d2a6240cf7a777d876ed565d9))
* restore full docker build workflow with release link ([7044b83](https://github.com/szpaczyna/whoops/commit/7044b83ad81c576c85c451e441acb3c453e5ad52))
* simplify docker build workflow for testing ([1b18bef](https://github.com/szpaczyna/whoops/commit/1b18bef6f0a92426682a3333878cb9fb69acf2c4))
* tag images with semver on tag pushes ([c6b51f2](https://github.com/szpaczyna/whoops/commit/c6b51f22236ade12cfbec62e98f60a0c5b7da3e7))
* trigger docker build ([58a867f](https://github.com/szpaczyna/whoops/commit/58a867fa364f3d33ef1bbe15bca89a5efa9f079b))
