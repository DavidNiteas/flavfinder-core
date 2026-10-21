"""Command-line interface for flavfinder-core."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from flavfinder import __version__
from flavfinder.config import TrainingConfig
from flavfinder.data import audit_frame, leakage_report
from flavfinder.evaluate import evaluate
from flavfinder.io import SpectrumSchema, read_frame, save_json
from flavfinder.predict import predict
from flavfinder.train import train


def _add_schema_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--mz-col", default=None)
    parser.add_argument("--intensity-col", default=None)
    parser.add_argument("--label-col", default=None)
    parser.add_argument("--id-col", default=None)


def _schema(args: argparse.Namespace) -> SpectrumSchema:
    return SpectrumSchema(
        mz_col=args.mz_col or "mz",
        intensity_col=args.intensity_col or "intensity",
        label_col=args.label_col or "label",
        id_col=args.id_col,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="flavfinder",
        description=(
            "Independent, code-only port of the flavfinder MS/MS flavonoid "
            "classifier."
        ),
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--describe", action="store_true", help="describe this port")
    subparsers = parser.add_subparsers(dest="command")

    audit_parser = subparsers.add_parser("audit", help="audit a spectrum table")
    audit_parser.add_argument("--input", help="single input table")
    audit_parser.add_argument("--train", help="training table for leakage analysis")
    audit_parser.add_argument("--test", help="test table for leakage analysis")
    audit_parser.add_argument("--output", help="write a JSON report")
    _add_schema_args(audit_parser)

    train_parser = subparsers.add_parser("train", help="train a model bundle")
    train_parser.add_argument("--config", help="YAML training config")
    train_parser.add_argument("--train", help="override training table")
    train_parser.add_argument("--validation", help="override validation table")
    train_parser.add_argument("--test", help="override test table")
    train_parser.add_argument("--output-dir", help="override output directory")
    train_parser.add_argument("--backend", help="autogluon, lightgbm, sklearn")
    train_parser.add_argument("--method", help="binning or tokenization")
    train_parser.add_argument("--seed", type=int)
    train_parser.add_argument("--overwrite", action="store_true")
    train_parser.add_argument("--no-bootstrap", action="store_true")
    train_parser.add_argument("--n-boot", type=int)
    _add_schema_args(train_parser)

    predict_parser = subparsers.add_parser("predict", help="score a spectrum table")
    predict_parser.add_argument("--model", required=True)
    predict_parser.add_argument("--input", required=True)
    predict_parser.add_argument("--output")
    _add_schema_args(predict_parser)

    evaluate_parser = subparsers.add_parser("evaluate", help="evaluate a model bundle")
    evaluate_parser.add_argument("--model", required=True)
    evaluate_parser.add_argument("--input", required=True)
    evaluate_parser.add_argument("--output")
    evaluate_parser.add_argument("--no-bootstrap", action="store_true")
    evaluate_parser.add_argument("--n-boot", type=int, default=1000)
    evaluate_parser.add_argument("--seed", type=int, default=42)
    _add_schema_args(evaluate_parser)

    return parser


def _cmd_audit(args: argparse.Namespace) -> int:
    schema = _schema(args)
    report: dict[str, object] = {}
    if args.train and args.test:
        train_frame = read_frame(args.train, schema)
        test_frame = read_frame(args.test, schema)
        report["train"] = audit_frame(train_frame, schema)
        report["test"] = audit_frame(test_frame, schema)
        report["leakage"] = leakage_report(train_frame, test_frame, schema)
    elif args.input:
        report["input"] = audit_frame(read_frame(args.input, schema), schema)
    else:
        raise ValueError("audit requires --input or both --train and --test")
    if args.output:
        save_json(report, args.output)
    print(f"audited {len(report)} section(s)")
    if args.output:
        print(f"wrote {args.output}")
    return 0


def _cmd_train(args: argparse.Namespace) -> int:
    config = TrainingConfig.from_yaml(args.config) if args.config else TrainingConfig()
    if args.mz_col:
        config.data.mz_col = args.mz_col
    if args.intensity_col:
        config.data.intensity_col = args.intensity_col
    if args.label_col:
        config.data.label_col = args.label_col
    if args.id_col:
        config.data.id_col = args.id_col
    if args.train:
        config.data.train = args.train
    if args.validation:
        config.data.validation = args.validation
    if args.test:
        config.data.test = args.test
    if args.output_dir:
        config.output_dir = args.output_dir
    if args.backend:
        config.model.backend = args.backend
    if args.method:
        config.preprocessing.method = args.method
    if args.seed is not None:
        config.seed = args.seed
        config.model.random_state = args.seed
    if args.overwrite:
        config.overwrite = True
    if args.no_bootstrap:
        config.with_bootstrap = False
    if args.n_boot is not None:
        config.n_boot = args.n_boot
    metrics = train(config)
    for split in ("train", "validation", "test"):
        if split in metrics:
            values = metrics[split]
            print(
                f"{split}: n={values['n']} auroc={values['auroc']} "
                f"auprc={values['auprc']}"
            )
    print(f"model written to {config.output_dir}")
    return 0


def _cmd_predict(args: argparse.Namespace) -> int:
    output = predict(
        args.model,
        args.input,
        args.output,
        schema=_schema(args),
    )
    print(f"scored {len(output)} spectrum(s)")
    if args.output:
        print(f"wrote {args.output}")
    return 0


def _cmd_evaluate(args: argparse.Namespace) -> int:
    metrics = evaluate(
        args.model,
        args.input,
        args.output,
        schema=_schema(args),
        with_bootstrap=not args.no_bootstrap,
        n_boot=args.n_boot,
        seed=args.seed,
    )
    print(
        f"n={metrics['n']} auroc={metrics['auroc']} "
        f"auprc={metrics['auprc']} brier={metrics['brier']}"
    )
    if args.output:
        print(f"wrote {args.output}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.describe:
        print(
            "flavfinder-core is an independent, code-only port of "
            "https://github.com/Ficere/flavfinder.\n"
            "It does not include training data, real example spectra, or "
            "pretrained models."
        )
        return 0
    if not args.command:
        parser.print_help()
        return 0
    handlers = {
        "audit": _cmd_audit,
        "train": _cmd_train,
        "predict": _cmd_predict,
        "evaluate": _cmd_evaluate,
    }
    try:
        return handlers[args.command](args)
    except (FileNotFoundError, FileExistsError, ImportError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
