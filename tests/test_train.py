import json
import pandas as pd
from linear_regression.training import train


def test_main_writes_versioned_model_and_metrics(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    models_dir = tmp_path / "models"
    data_dir.mkdir()

    pd.DataFrame({"x": [1, 2, 3, 4], "y": [2, 4, 6, 8]}).to_csv(data_dir / "train.csv", index=False)
    pd.DataFrame({"x": [5, 6], "y": [10, 12]}).to_csv(data_dir / "test.csv", index=False)

    monkeypatch.setattr(train, "DATA_DIR", data_dir)
    monkeypatch.setattr(train, "MODELS_DIR", models_dir)

    train.main()

    version = (models_dir / "latest.txt").read_text().strip()
    version_dir = models_dir / version

    assert (version_dir / "model.joblib").exists()

    metrics = json.loads((version_dir / "metrics.json").read_text())
    assert metrics["version"] == version
    assert metrics["n_train"] == 4
    assert metrics["n_test"] == 2
    assert metrics["features"] == ["x"]
    assert metrics["target"] == "y"