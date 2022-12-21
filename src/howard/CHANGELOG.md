# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Certificate issuer now has the organization as first level attribute

## [0.3.0-howard] - 2022-08-05

### Changed

- Enforce to use at least django-marion 0.4.0

## [0.2.7-howard] - 2022-01-25

### Fixed

- Fix syntax error within CertificateIssuer template

## [0.2.6-howard] - 2022-01-25

### Changed

- Update CertificateIssuer to add an optional `creation_date` field into context_query

## [0.2.5-howard] - 2021-11-29

### Changed

- Update InvoiceIssuer to generate both invoice and credit note
- Create a utils module to share code throughout the application

## [0.2.4-howard] - 2021-06-15

### Removed

- Useless course description on certificate template

## [0.2.3-howard] - 2021-06-11

### Fixed

- Fix path to compile translations after move local files

## [0.2.2-howard] - 2021-06-10

### Fixed

- Fix translation typo in the `certificate` document

## [0.2.1-howard] - 2021-06-09

### Fixed

- Upgrade `django-marion` dependency to `0.3.0`
- Move local files to `howard` Django project location

## [0.2.0-howard] - 2021-06-08

### Added

- Add certificate issuer
- Rename and resize FUN logo
- Add invoice issuer

### Fixed

- Add package description (README)

## [0.1.2-howard] - 2021-04-06

### Fixed

- Include templates and static files in distributed package

## [0.1.1-howard] - 2021-04-06

### Changed

- Upgrade `django-marion` dependency to `0.1.1`

### Fixed

- Package name in version metadata

## [0.1.0-howard] - 2021-03-26

### Added

- Draft realisation certificate issuer

[unreleased]: https://github.com/openfun/marion/compare/v0.3.0-howard...master
[0.3.0-howard]: https://github.com/openfun/marion/compare/v0.2.7-howard...v0.3.0-howard
[0.2.7-howard]: https://github.com/openfun/marion/compare/v0.2.6-howard...v0.2.7-howard
[0.2.6-howard]: https://github.com/openfun/marion/compare/v0.2.5-howard...v0.2.6-howard
[0.2.5-howard]: https://github.com/openfun/marion/compare/v0.2.4-howard...v0.2.5-howard
[0.2.4-howard]: https://github.com/openfun/marion/compare/v0.2.3-howard...v0.2.4-howard
[0.2.3-howard]: https://github.com/openfun/marion/compare/v0.2.2-howard...v0.2.3-howard
[0.2.2-howard]: https://github.com/openfun/marion/compare/v0.2.1-howard...v0.2.2-howard
[0.2.1-howard]: https://github.com/openfun/marion/compare/v0.2.0-howard...v0.2.1-howard
[0.2.0-howard]: https://github.com/openfun/marion/compare/v0.1.2-howard...v0.2.0-howard
[0.1.2-howard]: https://github.com/openfun/marion/compare/v0.1.1-howard...v0.1.2-howard
[0.1.1-howard]: https://github.com/openfun/marion/compare/v0.1.0-howard...v0.1.1-howard
[0.1.0-howard]: https://github.com/openfun/marion/compare/090add7...v0.1.0-howard
