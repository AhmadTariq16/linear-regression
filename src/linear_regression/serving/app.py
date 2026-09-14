from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

REPO_ROOT = Path(__file__).resolve().parents[3]
MODELS_DIR = REPO_ROOT / "models"

model = None
model_version: str | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, model_version
    latest_path = MODELS_DIR / "latest.txt"
    if latest_path.exists():
        version = latest_path.read_text().strip()
        model_path = MODELS_DIR / version / "model.joblib"
        if model_path.exists():
            model = joblib.load(model_path)
            model_version = version
    yield


app = FastAPI(lifespan=lifespan)


class PredictRequest(BaseModel):
    x: float


class PredictResponse(BaseModel):
    prediction: float


class VersionResponse(BaseModel):
    version: str | None


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Run the training job first.",
        )
    prediction = model.predict([[request.x]])[0]
    return PredictResponse(prediction=prediction)


@app.get("/version", response_model=VersionResponse)
def version() -> VersionResponse:
    return VersionResponse(version=model_version)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ok"}


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
