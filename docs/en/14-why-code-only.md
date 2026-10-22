# Why this repository is code-only

**Level:** 0 — Scope  
**Prerequisites:** none.

`flavfinder-core` deliberately ships **code only**. This page explains the two
decisions behind that scope: no pretrained model weights and no bundled training
data.

## 1. We do not ship model weights

A fitted model bundle can be large, especially an AutoGluon predictor with
multiple model families. Shipping one would:

- make the repository heavy and awkward to clone,
- freeze a model trained on an older, instrument-specific snapshot,
- encourage users to apply a model outside its validation domain.

Training this pipeline is reproducible and feasible on a single workstation;
the exact cost depends on data size, feature width, backend, and CPU. We ship the
configs, training code, evaluation code, and model metadata so users can train on
their own spectra and keep the artifact locally or in their own storage.

If you need a pretrained model for a regulated or production workflow, train and
validate it on your own representative data, then version it separately.

## 2. We do not ship training data

The data used during development is an older reference snapshot. Public MS/MS
libraries are larger and fresher:

- **GNPS** — community spectral libraries and molecular networks
- **MassBank** — public MS/MS reference spectra
- **MoNA** — MassBank of North America
- **NIST / METLIN** — licensed libraries, where applicable

Using a frozen snapshot would anchor users to old labels, old instruments, and an
old class balance. It is better to build a dataset from current public records.

Public data is not plug-and-play, however. You still need to:

- link each spectrum to a structure (SMILES/InChIKey),
- filter by ion mode, instrument, collision energy, and quality,
- remove duplicates and conflicting labels,
- validate the flavonoid/non-flavonoid labels,
- split by compound or near-duplicate group, not randomly.

## 3. What we provide instead

We provide the **labeling and training toolkit**:

```bash
flavfinder label --input raw_with_smiles.csv --output labeled.csv --report label_report.json
flavfinder train --train labeled.csv --test heldout.csv --output-dir artifacts/model
```

The `label` command uses RDKit and a subclass-aware SMARTS ruleset. It outputs a
binary label, the matched subclass, canonical SMILES, InChIKey, and an error
field for invalid structures.

## 4. What the labels mean

The RDKit rules are **scaffold-level heuristics**, not a formal taxonomy. They
cover common flavonoid families:

- flavonols, flavones, flavanones, flavanonols
- flavan-3-ols (catechins)
- isoflavones
- chalcones and dihydrochalcones
- aurones
- anthocyanidins

A molecule is labeled positive if it matches at least one rule. The first match
in rule order becomes `flavonoid_subclass`; all matches are recorded in
`matched_patterns`.

This is useful for rapidly building a training set, but it is not a substitute
for an expert-curated taxonomy. Validate a sample against NPClassifier,
ClassyFire, or manual review before treating the labels as ground truth.

## 5. Recommended workflow

1. Collect MS/MS + SMILES records from a public library you are allowed to use.
2. Label with `flavfinder label`.
3. Remove invalid SMILES and inspect the label report.
4. Deduplicate by InChIKey and spectrum content.
5. Split by compound/InChIKey or near-duplicate group.
6. Train positive and negative ion modes separately.
7. Evaluate with AUPRC, calibration, and an external test set.

Continue with [Build your own dataset](./15-build-your-own-dataset.md).

**Next:** [Build your own dataset](./15-build-your-own-dataset.md)
