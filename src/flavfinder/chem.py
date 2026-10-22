"""RDKit-based flavonoid labeling for building custom training datasets.

The labeler is intentionally rule-based and subclass-aware. A single
"flavonoid core" SMARTS would miss flavan-3-ols, isoflavones, chalcones,
aurones, and anthocyanidins, so the default ruleset matches several scaffold
families and reports which patterns fired.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

try:  # optional dependency
    from rdkit import Chem
    from rdkit.Chem.MolStandardize import rdMolStandardize
except ImportError:  # pragma: no cover - exercised when rdkit is absent
    Chem = None  # type: ignore[assignment]
    rdMolStandardize = None  # type: ignore[assignment]


DEFAULT_PATTERNS: dict[str, dict[str, str]] = {
    "flavonol": {
        "smarts": "O=c1c(O)c(-c2ccccc2)oc2ccccc12",
        "description": "3-hydroxyflavone / flavonol scaffold (quercetin, kaempferol)",
    },
    "flavone": {
        "smarts": "O=c1cc(-c2ccccc2)oc2ccccc12",
        "description": "2-phenylchromen-4-one scaffold (apigenin, luteolin)",
    },
    "dihydroflavonol": {
        "smarts": "O=C1C(O)C(c2ccccc2)Oc2ccccc12",
        "description": "flavanonol / 3-hydroxyflavanone scaffold (taxifolin)",
    },
    "flavanone": {
        "smarts": "O=C1CC(c2ccccc2)Oc2ccccc12",
        "description": "2-phenylchroman-4-one scaffold (naringenin, hesperetin)",
    },
    "flavan3ol": {
        "smarts": "OC1Cc2ccccc2OC1c1ccccc1",
        "description": "flavan-3-ol scaffold (catechin, epicatechin)",
    },
    "isoflavone": {
        "smarts": "O=c1c(-c2ccccc2)coc2ccccc12",
        "description": "3-phenylchromen-4-one scaffold (genistein, daidzein)",
    },
    "chalcone": {
        "smarts": "[CX3;!R](=O)(C=Cc1ccccc1)c1ccccc1",
        "description": "open-chain 1,3-diphenylprop-2-en-1-one scaffold",
    },
    "dihydrochalcone": {
        "smarts": "[CX3;!R](=O)(CCc1ccccc1)c1ccccc1",
        "description": "open-chain 1,3-diphenylpropan-1-one scaffold",
    },
    "aurone": {
        "smarts": "O=C1C(=Cc2ccccc2)Oc2ccccc12",
        "description": "benzofuran-3-one / aurone scaffold",
    },
    "anthocyanidin": {
        "smarts": "[o+]1c(-c2ccccc2)ccc2ccccc12",
        "description": "flavylium / anthocyanidin scaffold (cyanidin, delphinidin)",
    },
}


def _require_rdkit() -> None:
    if Chem is None or rdMolStandardize is None:
        raise ImportError(
            "RDKit is optional; install with: pip install 'flavfinder-core[chem]'"
        )


@dataclass(frozen=True)
class LabelResult:
    input_smiles: str
    canonical_smiles: str | None
    inchikey: str | None
    label: int | None
    subclass: str | None
    matched_patterns: tuple[str, ...]
    error: str | None

    @property
    def valid(self) -> bool:
        return self.error is None


class FlavonoidLabeler:
    """Match RDKit molecules against a prioritized flavonoid SMARTS ruleset."""

    def __init__(
        self,
        patterns: Mapping[str, str | Mapping[str, str]] | None = None,
        *,
        standardize: bool = True,
    ) -> None:
        _require_rdkit()
        raw = patterns or DEFAULT_PATTERNS
        self.patterns: dict[str, str] = {}
        for name, value in raw.items():
            smarts = value["smarts"] if isinstance(value, Mapping) else str(value)
            self.patterns[str(name)] = smarts
        self._compiled = {}
        for name, smarts in self.patterns.items():
            pattern = Chem.MolFromSmarts(smarts)
            if pattern is None:
                raise ValueError(f"invalid SMARTS for pattern {name!r}: {smarts}")
            self._compiled[name] = pattern
        self.standardize = bool(standardize)

    @classmethod
    def from_yaml(cls, path: str | Path) -> FlavonoidLabeler:
        with Path(path).open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        patterns = data.get("patterns", data)
        if not isinstance(patterns, dict):
            raise ValueError("pattern YAML must contain a mapping")
        return cls(patterns)

    def _standardize_mol(self, mol: Any) -> Any:
        if not self.standardize:
            return mol
        try:
            mol = rdMolStandardize.Cleanup(mol)
            chooser = rdMolStandardize.LargestFragmentChooser()
            mol = chooser.choose(mol)
        except Exception:
            return mol
        return mol

    def label_smiles(self, smiles: Any) -> LabelResult:
        _require_rdkit()
        text = "" if smiles is None else str(smiles).strip()
        if not text:
            return LabelResult(text, None, None, None, None, (), "empty SMILES")
        mol = Chem.MolFromSmiles(text)
        if mol is None:
            return LabelResult(text, None, None, None, None, (), "invalid SMILES")
        mol = self._standardize_mol(mol)
        if mol is None:
            return LabelResult(text, None, None, None, None, (), "standardization failed")
        canonical = Chem.MolToSmiles(mol, canonical=True)
        try:
            inchikey = Chem.MolToInchiKey(mol)
        except Exception:
            inchikey = None
        matches = tuple(
            name
            for name, pattern in self._compiled.items()
            if mol.HasSubstructMatch(pattern)
        )
        subclass = matches[0] if matches else None
        return LabelResult(
            input_smiles=text,
            canonical_smiles=canonical,
            inchikey=inchikey,
            label=1 if matches else 0,
            subclass=subclass,
            matched_patterns=matches,
            error=None,
        )

    def label_frame(
        self,
        frame: pd.DataFrame,
        *,
        smiles_col: str = "smiles",
        label_col: str = "label",
    ) -> pd.DataFrame:
        if smiles_col not in frame.columns:
            raise ValueError(f"missing SMILES column: {smiles_col!r}")
        results = [self.label_smiles(value) for value in frame[smiles_col]]
        output = frame.copy()
        output["smiles_canonical"] = [result.canonical_smiles for result in results]
        output["inchikey"] = [result.inchikey for result in results]
        output["flavonoid_label"] = pd.array(
            [result.label for result in results], dtype="Int64"
        )
        output["flavonoid_subclass"] = [result.subclass for result in results]
        output["matched_patterns"] = [
            "|".join(result.matched_patterns) for result in results
        ]
        output["smiles_error"] = [result.error for result in results]
        if label_col in output.columns:
            output[f"{label_col}_original"] = output[label_col]
        output[label_col] = output["flavonoid_label"]
        return output

    def summary(self, frame: pd.DataFrame) -> dict[str, Any]:
        if "flavonoid_label" not in frame.columns:
            raise ValueError("frame has not been labeled")
        labels = frame["flavonoid_label"]
        valid = labels.notna()
        positives = int((labels == 1).sum())
        negatives = int((labels == 0).sum())
        subclasses = (
            frame.loc[valid, "flavonoid_subclass"]
            .dropna()
            .value_counts()
            .to_dict()
        )
        duplicate_groups = 0
        duplicate_rows = 0
        if "inchikey" in frame.columns:
            keys = frame.loc[valid, "inchikey"].dropna()
            counts = keys.value_counts()
            duplicate_groups = int((counts > 1).sum())
            duplicate_rows = int(counts[counts > 1].sum())
        return {
            "n_total": int(len(frame)),
            "n_valid": int(valid.sum()),
            "n_invalid": int((~valid).sum()),
            "n_positive": positives,
            "n_negative": negatives,
            "positive_rate": float(positives / valid.sum()) if valid.sum() else None,
            "subclass_counts": {str(k): int(v) for k, v in subclasses.items()},
            "duplicate_inchikey_groups": duplicate_groups,
            "duplicate_inchikey_rows": duplicate_rows,
        }


def label_frame(
    frame: pd.DataFrame,
    *,
    smiles_col: str = "smiles",
    label_col: str = "label",
    patterns: Mapping[str, str | Mapping[str, str]] | None = None,
) -> pd.DataFrame:
    """Convenience wrapper around :class:`FlavonoidLabeler`."""

    return FlavonoidLabeler(patterns).label_frame(
        frame, smiles_col=smiles_col, label_col=label_col
    )


__all__ = [
    "DEFAULT_PATTERNS",
    "FlavonoidLabeler",
    "LabelResult",
    "label_frame",
]
