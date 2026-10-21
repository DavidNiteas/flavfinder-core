# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-22

### Added

- Bootstrap of the independent, code-only `flavfinder-core` repository.
- MIT license, provenance notice, authors file, and citation metadata.
- Package skeleton, minimal CLI, and release guard hooks.
- Spectrum I/O and validation (CSV/JSON, strings or numeric sequences).
- Binning and tokenization preprocessing with JSON persistence.
- Pluggable AutoGluon, LightGBM, and scikit-learn backends.
- Config-driven training, prediction, evaluation, and threshold selection.
- Data auditing: exact/near duplicates, leakage reports, and group-aware splits.
- Stratified group split (`StratifiedGroupKFold`) with a greedy fallback.
- Bilingual progressive documentation under `docs/en` and `docs/zh-CN`.
- Code-only Dockerfile and `.dockerignore`.
- Synthetic-data test suite covering preprocessing, metrics, pipeline, CLI, and audit.
