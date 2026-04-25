from __future__ import annotations

from pathlib import Path
import argparse

import pandas as pd
import yaml
from sklearn.linear_model import Ridge


def read_csv_with_fallback(path: str | Path) -> pd.DataFrame:
    for enc in ("utf-8", "cp932", "shift_jis"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path)


def load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_submission(config_path: Path) -> Path:
    config = load_config(config_path)
    paths = config["paths"]
    target_column = config.get("target", {}).get("column", "含水率")
    seed = int(config.get("seed", 42))

    train_df = read_csv_with_fallback(paths["train_csv"])
    test_df = read_csv_with_fallback(paths["test_csv"])

    if target_column in train_df.columns:
        y = train_df[target_column]
    else:
        y = train_df.iloc[:, 3]

    # Train has: [id, species_no, species_name, target, ...spectra]
    # Test has:  [id, species_no, species_name, ...spectra]
    x_train = train_df.iloc[:, 4:]
    x_test = test_df.iloc[:, 3:]

    model = Ridge(alpha=1.0, random_state=seed)
    model.fit(x_train, y)
    preds = model.predict(x_test)

    output_path = Path(paths["output_submission_csv"])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    submission_df = pd.DataFrame(
        {
            "sample number": test_df.iloc[:, 0],
            "prediction": preds,
        }
    )
    submission_df.to_csv(output_path, index=False, header=False)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate baseline submission CSV.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/default.yaml"),
        help="Path to config file.",
    )
    args = parser.parse_args()

    output_path = build_submission(args.config)
    print(f"submission generated: {output_path}")


if __name__ == "__main__":
    main()
