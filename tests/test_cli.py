from __future__ import annotations

import json

import pytest

from flavfinder.cli import main


def test_cli_describe(capsys) -> None:
    assert main(["--describe"]) == 0
    out = capsys.readouterr().out
    assert "independent" in out


def test_cli_train_predict_evaluate_audit(tmp_path, synthetic_csv, capsys) -> None:
    model_dir = tmp_path / "model"
    assert (
        main(
            [
                "train",
                "--train",
                synthetic_csv,
                "--test",
                synthetic_csv,
                "--output-dir",
                str(model_dir),
                "--backend",
                "sklearn",
                "--no-bootstrap",
                "--overwrite",
            ]
        )
        == 0
    )
    assert (model_dir / "metadata.json").exists()

    prediction_path = tmp_path / "prediction.json"
    assert (
        main(
            [
                "predict",
                "--model",
                str(model_dir),
                "--input",
                synthetic_csv,
                "--output",
                str(prediction_path),
            ]
        )
        == 0
    )
    predictions = json.loads(prediction_path.read_text())
    assert len(predictions) > 0
    assert "score" in predictions[0]

    metrics_path = tmp_path / "metrics.json"
    assert (
        main(
            [
                "evaluate",
                "--model",
                str(model_dir),
                "--input",
                synthetic_csv,
                "--output",
                str(metrics_path),
                "--no-bootstrap",
            ]
        )
        == 0
    )
    assert "auroc" in json.loads(metrics_path.read_text())

    audit_path = tmp_path / "audit.json"
    assert (
        main(
            [
                "audit",
                "--train",
                synthetic_csv,
                "--test",
                synthetic_csv,
                "--output",
                str(audit_path),
            ]
        )
        == 0
    )
    audit = json.loads(audit_path.read_text())
    assert audit["leakage"]["overlap_n"] > 0
    capsys.readouterr()


def test_cli_error_returns_two(tmp_path) -> None:
    assert (
        main(
            [
                "train",
                "--train",
                str(tmp_path / "missing.csv"),
                "--output-dir",
                str(tmp_path / "model"),
            ]
        )
        == 2
    )


def test_cli_label(tmp_path) -> None:
    pytest.importorskip("rdkit")
    input_path = tmp_path / "smiles.csv"
    input_path.write_text(
        "id,smiles\n"
        "q1,O=c1c(O)c(-c2ccc(O)c(O)c2)oc2cc(O)cc(O)c12\n"
        "c1,Cn1cnc2c1c(=O)n(C)c(=O)n2C\n"
        "bad,not-a-smiles\n"
    )
    output_path = tmp_path / "labeled.csv"
    report_path = tmp_path / "report.json"
    assert (
        main(
            [
                "label",
                "--input",
                str(input_path),
                "--output",
                str(output_path),
                "--report",
                str(report_path),
            ]
        )
        == 0
    )
    labeled = output_path.read_text()
    assert "flavonoid_subclass" in labeled
    assert "flavonol" in labeled
    report = json.loads(report_path.read_text())
    assert report["n_total"] == 3
    assert report["n_valid"] == 2
    assert report["n_invalid"] == 1
