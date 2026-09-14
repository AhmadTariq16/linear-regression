from fastapi.testclient import TestClient

from linear_regression.serving.app import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_503_when_model_not_loaded(monkeypatch):
    monkeypatch.setattr("linear_regression.serving.app.model", None)
    response = client.get("/ready")
    assert response.status_code == 503


def test_ready_returns_ok_when_model_loaded(monkeypatch):
    monkeypatch.setattr("linear_regression.serving.app.model", object())
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


class FakeModel:
    def predict(self, X):
        return [42.0]


def test_predict_returns_503_when_model_not_loaded(monkeypatch):
    monkeypatch.setattr("linear_regression.serving.app.model", None)
    response = client.post("/predict", json={"x": 1.0})
    assert response.status_code == 503


def test_predict_returns_prediction_when_model_loaded(monkeypatch):
    monkeypatch.setattr("linear_regression.serving.app.model", FakeModel())
    response = client.post("/predict", json={"x": 1.0})
    assert response.status_code == 200
    assert response.json() == {"prediction": 42.0}


def test_version_returns_none_when_no_model_loaded(monkeypatch):
    monkeypatch.setattr("linear_regression.serving.app.model_version", None)
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": None}


def test_version_returns_current_version_when_loaded(monkeypatch):
    monkeypatch.setattr("linear_regression.serving.app.model_version", "20260101T000000Z")
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": "20260101T000000Z"}