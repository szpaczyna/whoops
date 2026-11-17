# Changelog

## [1.3.2](https://github.com/szpaczyna/whoops/compare/v1.3.1...v1.3.2) (2026-11-17)


### Bug Fixes

* add timeouts to Whoop API requests ([#19](https://github.com/szpaczyna/whoops/issues/19)) ([0ef5eda](https://github.com/szpaczyna/whoops/commit/0ef5eda6b2a0797eec599ae8dd3325c725dc05e9))
* count rows instead of loading full tables on the index page ([#27](https://github.com/szpaczyna/whoops/issues/27)) ([a14db63](https://github.com/szpaczyna/whoops/commit/a14db631c629dc44b6bb4b32667d6bc7b6f4353b))
* log token restore and migration failures at startup ([#28](https://github.com/szpaczyna/whoops/issues/28)) ([05551d8](https://github.com/szpaczyna/whoops/commit/05551d8885e2d7df0ab6e3e00e38aff7b6c9d6d8))
* publish ports on localhost only in the compose template ([#20](https://github.com/szpaczyna/whoops/issues/20)) ([07f5665](https://github.com/szpaczyna/whoops/commit/07f5665cd2f324f0737483c8ffcc54bafe8c79ff))
* re-queue failed import tasks without retrying the worker ([#23](https://github.com/szpaczyna/whoops/issues/23)) ([9dd0146](https://github.com/szpaczyna/whoops/commit/9dd0146210d45fe2e5a9f50f6f1417c1cdb2484e))
* skip unscored sleeps and recoveries during import ([#18](https://github.com/szpaczyna/whoops/issues/18)) ([f876d7f](https://github.com/szpaczyna/whoops/commit/f876d7f3a1579711b63ec02340b34321dab82671))
* use a random single-use OAuth state ([#21](https://github.com/szpaczyna/whoops/issues/21)) ([4d33378](https://github.com/szpaczyna/whoops/commit/4d3337880c8beb69f1537fd2eac961f42cd85783))
* use Recreate strategy for the Kubernetes deployment ([#22](https://github.com/szpaczyna/whoops/issues/22)) ([9065f05](https://github.com/szpaczyna/whoops/commit/9065f05e7f4c1869f1c686c58fdbbc77d231e63a))


### Miscellaneous

* **deps:** update dependency apscheduler to v3.11.3 ([#10](https://github.com/szpaczyna/whoops/issues/10)) ([b8f4a33](https://github.com/szpaczyna/whoops/commit/b8f4a33ac81208f623bc623c5d822cc083881585))
* **deps:** update dependency cryptography to v50.0.2 ([#11](https://github.com/szpaczyna/whoops/issues/11)) ([ed1f4d1](https://github.com/szpaczyna/whoops/commit/ed1f4d1372b0424d0ceee0bb0716e82bb0d0acf6))
* **deps:** update dependency flask to v3.1.3 ([#13](https://github.com/szpaczyna/whoops/issues/13)) ([fa3c04d](https://github.com/szpaczyna/whoops/commit/fa3c04d9390e984b77b12330754ebc230dbdfb07))
* **deps:** update dependency flask-restful to v0.3.10 ([#14](https://github.com/szpaczyna/whoops/issues/14)) ([051b83c](https://github.com/szpaczyna/whoops/commit/051b83cfc32a8cdea823309ede3a6c9b12a5f30f))
* **deps:** update dependency psycopg2 to v2.9.13 ([#16](https://github.com/szpaczyna/whoops/issues/16)) ([08dc94c](https://github.com/szpaczyna/whoops/commit/08dc94c8a61eded40ef615877fa3fa3db742c67d))
* **deps:** update dependency pymysql to v1.2.4 ([#29](https://github.com/szpaczyna/whoops/issues/29)) ([20a5ab9](https://github.com/szpaczyna/whoops/commit/20a5ab97aec5de574256e890402545de1d684cc4))
* **deps:** update dependency requests to v2.33.0 [security] ([#33](https://github.com/szpaczyna/whoops/issues/33)) ([ebb5627](https://github.com/szpaczyna/whoops/commit/ebb5627d459860c8f1f155ba2b9fededac6acb74))
* remove unused export template ([#25](https://github.com/szpaczyna/whoops/issues/25)) ([9ad6899](https://github.com/szpaczyna/whoops/commit/9ad6899bffed76192d8055f31d37756debd9f360))


### Refactoring

* remove unused Whoop client methods ([#24](https://github.com/szpaczyna/whoops/issues/24)) ([94cd4c3](https://github.com/szpaczyna/whoops/commit/94cd4c3b341479c2cf35a171432ce57e9e4229a5))
* serve model routes from one REST resource ([#26](https://github.com/szpaczyna/whoops/issues/26)) ([37e3485](https://github.com/szpaczyna/whoops/commit/37e3485f4025e74c0ebcecd04db0e1fa13a9fe89))

## [1.3.1](https://github.com/szpaczyna/whoops/compare/v1.3.0...v1.3.1) (2026-11-16)


### Bug Fixes

* allow recoveries without spo2 and skip rows that violate constraints ([#15](https://github.com/szpaczyna/whoops/issues/15)) ([8eafe53](https://github.com/szpaczyna/whoops/commit/8eafe53efc7354688379041ba60839aab6e5695b))


### Miscellaneous

* ignore DL3018 for apk packages tracked by the base image ([cc60ac4](https://github.com/szpaczyna/whoops/commit/cc60ac49be5c35909b33c7248709f0e3455f4328))

## [1.3.0](https://github.com/szpaczyna/whoops/compare/v1.2.2...v1.3.0) (2026-11-16)


### Features

* fetch only the last INCREMENTAL_IMPORT_DAYS in the scheduled import, with limit=25 per page ([62184ed](https://github.com/szpaczyna/whoops/commit/62184ed271e696ef93e88a66861ff533ecba37cc))
* persist the daily import schedule and allow disabling it ([62184ed](https://github.com/szpaczyna/whoops/commit/62184ed271e696ef93e88a66861ff533ecba37cc))
* updated grafana dasbhoards ([c07d376](https://github.com/szpaczyna/whoops/commit/c07d37678118cd32825558304799b06091a8ba40))


### Bug Fixes

* disable docker build on push to main ([4e80d7d](https://github.com/szpaczyna/whoops/commit/4e80d7d3e57f8d2cf1b0b9f52649b1a0f7035151))
* upsert imported records and refresh token before expiry ([#9](https://github.com/szpaczyna/whoops/issues/9)) ([62184ed](https://github.com/szpaczyna/whoops/commit/62184ed271e696ef93e88a66861ff533ecba37cc))


### Miscellaneous

* upgrade setup python to v7 ([d152d12](https://github.com/szpaczyna/whoops/commit/d152d1205d1987cc35915f5695e923249bb7ebea))


### Documentation

* align kubernetes example with the helm chart ([62184ed](https://github.com/szpaczyna/whoops/commit/62184ed271e696ef93e88a66861ff533ecba37cc))

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
