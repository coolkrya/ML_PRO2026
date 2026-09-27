import time
import uuid
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import BackgroundTasks, FastAPI, HTTPException
from pydantic import BaseModel

from price_predicting import db
from price_predicting.config import settings


class Features(BaseModel):
    model_config = {"extra": "forbid"}

    Id : int | None
    MSSubClass : int | None
    MSZoning : str | None
    LotFrontage : float | None
    LotArea : int | None
    Street : str | None
    Alley : str | None
    LotShape : str | None
    LandContour : str | None
    Utilities : str | None
    LotConfig : str | None
    LandSlope : str | None
    Neighborhood : str | None
    Condition1 : str | None
    Condition2 : str | None
    BldgType : str | None
    HouseStyle : str | None
    OverallQual : int | None
    OverallCond : int | None
    YearBuilt : int | None
    YearRemodAdd : int | None
    RoofStyle : str | None
    RoofMatl : str | None
    Exterior1st : str | None
    Exterior2nd : str | None
    MasVnrType : str | None
    MasVnrArea : float | None
    ExterQual : str | None
    ExterCond : str | None
    Foundation : str | None
    BsmtQual : str | None
    BsmtCond : str | None
    BsmtExposure : str | None
    BsmtFinType1 : str | None
    BsmtFinSF1 : int | None
    BsmtFinType2 : str | None
    BsmtFinSF2 : int | None
    BsmtUnfSF : int | None
    TotalBsmtSF : int | None
    Heating : str | None
    HeatingQC : str | None
    CentralAir : str | None
    Electrical : str | None
    FstFlrSF : int | None
    SndFlrSF : int | None
    LowQualFinSF : int | None
    GrLivArea : int | None
    BsmtFullBath : int | None
    BsmtHalfBath : int | None
    FullBath : int | None
    HalfBath : int | None
    BedroomAbvGr : int | None
    KitchenAbvGr : int | None
    KitchenQual : str | None
    TotRmsAbvGrd : int | None
    Functional : str | None
    Fireplaces : int | None
    FireplaceQu : str | None
    GarageType : str | None
    GarageYrBlt : float | None
    GarageFinish : str | None
    GarageCars : int | None
    GarageArea : int | None
    GarageQual : str | None
    GarageCond : str | None
    PavedDrive : str | None
    WoodDeckSF : int | None
    OpenPorchSF : int | None
    EnclosedPorch : int | None
    ThirdSsnPorch : int | None
    ScreenPorch : int | None
    PoolArea : int | None
    PoolQC : str | None
    Fence : str | None
    MiscFeature : str | None
    MiscVal : int | None
    MoSold : int | None
    YrSold : int | None
    SaleType : str | None
    SaleCondition : str | None
    


class Prediction(BaseModel):
    #model_config = {"protected_namespaces": ()}

    predicted_price: float
    model_version: str
    request_id: str
    latency_ms: float
    status_code: int


@asynccontextmanager
async def lifespan(app: FastAPI):
    bundle = joblib.load(settings.model_path)
    app.state.pipeline = bundle["pipeline"]
    app.state.meta = bundle["metadata"]
    app.state.version = bundle["metadata"]["version"]

    db.init()
    yield
    app.state.pipeline = None


app = FastAPI(title="House price prediction", version="1.0", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok", "model_version": getattr(app.state, "version", "unknown")}

@app.get("/ready")
def ready():
    if getattr(app.state, "pipeline", "None") is  None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {"status": "ready"}



@app.post("/v1/predict")
def predict(x: Features, bg: BackgroundTasks) -> Prediction:
    t0 = time.perf_counter()
    status_code = 200
    price = None
    payload = None
    request_id = str(uuid.uuid4())
    try:
        payload = x.model_dump()  # x.dict() in pydantic v1
        frame = pd.DataFrame([payload]).reindex(columns=app.state.meta["features"])

        price = float(app.state.pipeline.predict(frame)[0])

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
  
    except Exception as e:
        status_code = 500
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        raise HTTPException(status_code=status_code, detail=e)

    finally:
        bg.add_task(db.save_prediction, request_id, payload, price, app.state.version, latency_ms, status_code)

    return Prediction(predicted_price=price, model_version=app.state.version, request_id=request_id, latency_ms=latency_ms, status_code=status_code)


#@app.get("")





