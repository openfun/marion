# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `IssuerChoice` model to specify a path and a label for each issuer
- New migration file

### Fixed

- Update the `issuer` field of `DocumentRequest` to be a ForeignKey to the 
  `IssuerChoice` model, along with the required changes to other files within
  the project

### Removed

- the `defaults.py` file from howard, as it is no longer needed

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

[unreleased]: https://github.com/openfun/marion/compare/v0.3.0...master
[0.3.0]: https://github.com/openfun/marion/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/openfun/marion/compare/v0.1.2...v0.2.0
[0.1.2]: https://github.com/openfun/marion/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/openfun/marion/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/openfun/marion/compare/ebaa308...v0.1.0
