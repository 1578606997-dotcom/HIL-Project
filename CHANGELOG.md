# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.2.5] - 2026-02-25
### Added
- Internationalized project documentation with an English-first README and
  concise Chinese summary.
- Clear onboarding guidance for dependency setup and common runtime issues.

### Changed
- Refined global positioning language for HIL-Gateway as a token-optimization
  protocol in SLM→LLM cascade architectures.

## [v0.2] - 2026-02-25
### Added
- Architecture upgrade for SLM→LLM cascade workflows.
- Support for complex RAG-focused objects in HIL commands, including `@vs`
  (compare and contrast) and `@top` (top competitive advantages).
- Reverse translation path from natural language to HIL commands.

### Changed
- Parser and decoder behavior expanded to handle parameterized object forms,
  such as `@vs(Apple, Tesla)`.

## [v0.1] - 2026-02-25
### Added
- Initial HIL specification with core action, object, modifier, and parameter
  mappings.
- First transcoder implementation for parse/decode workflows.
- Baseline benchmarking script to compare token usage between natural language
  and HIL commands.
