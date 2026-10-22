from __future__ import annotations

import pandas as pd
import pytest

pytest.importorskip("rdkit")

from flavfinder.chem import FlavonoidLabeler, label_frame  # noqa: E402

POSITIVES = {
    "quercetin": "O=c1c(O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12",
    "naringenin": "O=C1CC(c2ccc(O)cc2)Oc2cc(O)cc(O)c12",
    "catechin": "Oc1cc2c(cc1O)OC(c1ccc(O)c(O)c1)C(O)C2",
    "genistein": "O=c1c(-c2ccc(O)cc2)coc2cc(O)cc(O)c12",
    "chalcone": "O=C(C=Cc1ccccc1)c1ccccc1",
    "taxifolin": "O=C1C(O)C(c2ccc(O)c(O)c2)Oc2cc(O)cc(O)c12",
    "cyanidin": "C1=CC(=CC=C1C2=[O+]C3=CC(=CC(=C3C=C2)O)O)O",
    "aureusidin": "O=C1C(=Cc2ccc(O)c(O)c2)Oc2cc(O)cc(O)c12",
}

NEGATIVES = {
    "coumarin": "O=c1ccc2ccccc2o1",
    "chromone": "O=c1ccoc2ccccc12",
    "warfarin": "CC(=O)CC(c1ccccc1)c1c(O)c2ccccc2oc1=O",
    "caffeine": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
    "aspirin": "CC(=O)Oc1ccccc1C(=O)O",
    "glucose": "OC[C@H]1OC(O)[C@H](O)[C@@H](O)[C@@H]1O",
    "cholesterol": "CC(C)CCCC(C)C1CCC2C1(CCC3C2CC=C4C3(CCC(C4)O)C)C",
}


@pytest.mark.parametrize("name,smiles", POSITIVES.items())
def test_positive_scaffolds(name: str, smiles: str) -> None:
    result = FlavonoidLabeler().label_smiles(smiles)
    assert result.label == 1, (name, result)
    assert result.subclass is not None
    assert result.matched_patterns
    assert result.error is None


@pytest.mark.parametrize("name,smiles", NEGATIVES.items())
def test_negative_controls(name: str, smiles: str) -> None:
    result = FlavonoidLabeler().label_smiles(smiles)
    assert result.label == 0, (name, result)
    assert result.matched_patterns == ()


def test_subclass_priority() -> None:
    result = FlavonoidLabeler().label_smiles(POSITIVES["quercetin"])
    assert result.subclass == "flavonol"
    assert "flavone" in result.matched_patterns


def test_invalid_smiles() -> None:
    result = FlavonoidLabeler().label_smiles("not-a-smiles")
    assert result.label is None
    assert result.error == "invalid SMILES"


def test_label_frame_preserves_existing_label() -> None:
    frame = pd.DataFrame(
        {
            "smiles": [POSITIVES["quercetin"], NEGATIVES["caffeine"], "bad"],
            "label": [0, 1, 0],
        }
    )
    labeled = label_frame(frame)
    assert labeled["label"].iloc[0] == 1
    assert labeled["label"].iloc[1] == 0
    assert pd.isna(labeled["label"].iloc[2])
    assert list(labeled["label_original"]) == [0, 1, 0]
    assert labeled["flavonoid_subclass"].iloc[0] == "flavonol"
    summary = FlavonoidLabeler().summary(labeled)
    assert summary["n_total"] == 3
    assert summary["n_valid"] == 2
    assert summary["n_invalid"] == 1
    assert summary["n_positive"] == 1
    assert summary["n_negative"] == 1


def test_custom_pattern_yaml(tmp_path) -> None:
    path = tmp_path / "patterns.yaml"
    path.write_text(
        "patterns:\n"
        "  only_phenyl:\n"
        "    smarts: 'c1ccccc1'\n"
        "    description: 'test pattern'\n"
    )
    labeler = FlavonoidLabeler.from_yaml(path)
    result = labeler.label_smiles("c1ccccc1")
    assert result.label == 1
    assert result.subclass == "only_phenyl"
