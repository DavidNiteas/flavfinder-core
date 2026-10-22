# Why there are no data or model files

**Level:** 0 — Scope  
**Prerequisites:** none.

The repo ships code. It doesn't include trained weights or training data. Two
reasons.

## Model bundles are large

An AutoGluon predictor with several model families can be hundreds of megabytes.
Committing it makes the repo heavy, freezes a model trained on one old snapshot,
and makes it easy to use the model outside the data it was validated on.

Training is reproducible. On a workstation it takes minutes to tens of minutes,
depending on data size, feature width, and backend. It's usually easier to
retrain on your own spectra than to pass a bundle around. For production, train
and validate on your own data, then version the artifact separately.

## Bundled data goes stale

The data used during development is an old snapshot. Public MS/MS libraries are
bigger and fresher:

- **GNPS** — community libraries and molecular networks
- **MassBank** — public reference spectra
- **MoNA** — MassBank of North America
- **NIST / METLIN** — licensed libraries, where applicable

Bundling the old data would tie you to old labels, old instruments, and an old
class balance. It's better to start from current public records.

Public data still needs work:

- link each spectrum to a structure (SMILES/InChIKey),
- filter by ion mode, instrument, collision energy, and quality,
- remove duplicates and conflicting labels,
- check the flavonoid/non-flavonoid labels,
- split by compound or near-duplicate group, not at random.

## What's in the repo instead

Labeling and training code:

```bash
flavfinder label --input raw_with_smiles.csv --output labeled.csv --report label_report.json
flavfinder train --train labeled.csv --test heldout.csv --output-dir artifacts/model
```

`flavfinder label` uses RDKit and a small SMARTS ruleset. It writes a binary
label, the matched scaffold family, canonical SMILES, InChIKey, and an error for
invalid structures.

## What the labels mean

The rules match scaffolds, not a formal taxonomy. They cover:

- flavonols, flavones, flavanones, flavanonols
- flavan-3-ols (catechins)
- isoflavones
- chalcones and dihydrochalcones
- aurones
- anthocyanidins

A molecule is positive if it matches at least one rule. The first match in rule
order becomes `flavonoid_subclass`; all matches go into `matched_patterns`.

They're a quick first pass. Spot-check against NPClassifier, ClassyFire, or by
hand before using them as ground truth.

## Workflow

1. Collect MS/MS + SMILES records from a library you're allowed to use.
2. Run `flavfinder label`.
3. Drop invalid SMILES and look at the label report.
4. Deduplicate by InChIKey and spectrum content.
5. Split by compound/InChIKey or near-duplicate group.
6. Train positive and negative ion modes separately.
7. Evaluate with AUPRC, calibration, and an external test set.

**Next:** [Build your own dataset](./15-build-your-own-dataset.md)
