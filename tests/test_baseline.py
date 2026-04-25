from pathlib import Path

import pandas as pd

from src.baseline import build_submission, read_csv_with_fallback


def test_submission_format_matches_test_rows(tmp_path: Path) -> None:
    output_file = tmp_path / "baseline_submission.csv"
    config_file = tmp_path / "config.yaml"

    config_file.write_text(
        "\n".join(
            [
                "seed: 42",
                "paths:",
                "  train_csv: data/raw/train.csv",
                "  test_csv: data/raw/test.csv",
                "  sample_submit_csv: data/raw/sample_submit.csv",
                f"  output_submission_csv: {output_file}",
                "target:",
                "  column: 含水率",
            ]
        ),
        encoding="utf-8",
    )

    generated_path = build_submission(config_file)
    assert generated_path.exists()

    test_df = read_csv_with_fallback("data/raw/test.csv")
    submit_df = pd.read_csv(generated_path, header=None)
    sample_df = pd.read_csv("data/raw/sample_submit.csv", header=None)

    assert submit_df.shape[0] == test_df.shape[0]
    assert submit_df.shape[1] == 2
    assert submit_df.shape == sample_df.shape
