# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2023-09-19

### Added

- Add Pydantic 2.2.0 compatibility

## [0.5.0] - 2023-05-23

### Added

- Add Django 4.2 compatibility
- Add `pdf_options` argument to `AbstractDocument.create` method

## [0.4.0] - 2022-08-05

### Added

- Add Django 4.0 compatibility

### Fixed

- Use static storage class to open static files

## [0.3.2] - 2021-11-29

### Added

- Create a `IssuerLazyChoiceField` to be able to update issuer field choices
  without creating migrations.

### Changed

- Add a `persist` argument to `AbstractDocument.create` method

## [0.3.1] - 2021-09-02

### Added

- `Weasyprint` 53.0+ is now needed

## [0.3.0] - 2021-06-08

### Added

- the `DocumentRequest` model now has a `get_document_path` helper

### Fixed

- Avoid caching pydantic model instance in the `PydanticModelField` to avoid
  multiple models collisions

## [0.2.0] - 2021-04-14

### Added

- Add Django 3.2 compatibility
- Distribute a complete documentation

### Fixed

- Add package description (README)

## [0.1.2] - 2021-04-06

### Fixed

- Include templates and static files in distributed package

## [0.1.1] - 2021-04-06

### Fixed

- Package name in version metadata

## [0.1.0] - 2021-03-26

### Added

- Install security updates in project Docker images
- Add `DocumentRequest` model, serializer and API viewset
- Add `DummyDocument` example document issuer
- Implement document issuer pattern

[unreleased]: https://github.com/openfun/marion/compare/v0.6.0...master
[0.6.0]: https://github.com/openfun/marion/compare/v0.5.0...0.6.0
[0.5.0]: https://github.com/openfun/marion/compare/v0.4.0...0.5.0
[0.4.0]: https://github.com/openfun/marion/compare/v0.3.2...0.4.0
[0.3.2]: https://github.com/openfun/marion/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/openfun/marion/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/openfun/marion/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/openfun/marion/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/openfun/marion/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/openfun/marion/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/openfun/marion/compare/ebaa308...v0.1.0
