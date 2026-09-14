import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = REPO_ROOT / "data"
MODELS_DIR = REPO_ROOT / "models"


def main() -> None:
    train_df = pd.read_csv(DATA_DIR / "train.csv").dropna()
    test_df = pd.read_csv(DATA_DIR / "test.csv").dropna()

    model = LinearRegression()
    model.fit(train_df[["x"]], train_df["y"])

    predictions = model.predict(test_df[["x"]])
    r2 = r2_score(test_df["y"], predictions)
    mse = mean_squared_error(test_df["y"], predictions)
    print(f"R2: {r2:.4f}")
    print(f"MSE: {mse:.4f}")

    version = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    version_dir = MODELS_DIR / version
    version_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, version_dir / "model.joblib")

    metrics = {"version": version,
               "n_train": len(train_df),
               "n_test": len(test_df),
               "features": ["x"],
               "target": "y",
               "r2_score": r2,
               "mse": mse}

    metrics_path = version_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)

    (MODELS_DIR / "latest.txt").write_text(version)
    print(f"Model version {version} saved to {version_dir}")


if __name__ == "__main__":
    main()