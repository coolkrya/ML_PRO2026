import time
import uuid
from contextlib import asynccontextmanager
from typing import Literal

import joblib
import pandas as pd
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from price_predicting import db
from price_predicting.config import settings

#dubinskiy dub

class Features(BaseModel):
    model_config = {"extra": "forbid"}

    Id: int 
    MSSubClass: int | None = Field(60, ge=0)
    MSZoning: Literal["A", "C", "FV", "I", "RH", "RL", "RP", "RM"] | None = "RL"
    LotFrontage: float | None = Field(65.0, ge=0)
    LotArea: int | None = Field(8450, ge=0)
    Street: Literal["Grvl", "Pave"] | None = "Pave"
    Alley: Literal["Grvl", "Pave", "NA", "nan"] | None = "nan"
    LotShape: Literal["IR1", "IR2", "IR3", "Reg"] | None = "Reg"
    LandContour: Literal["Bnk", "HLS", "Low", "Lvl"] | None = "Lvl"
    Utilities: Literal["AllPub", "NoSeWa"] | None = "AllPub"
    LotConfig: Literal["Corner", "CulDSac", "FR2", "FR3", "Inside"] | None = "Inside"
    LandSlope: Literal["Gtl", "Mod", "Sev"] | None = "Gtl"
    Neighborhood: Literal[
        "Blmngtn", "Blueste", "BrDale", "BrkSide", "ClearCr", "CollgCr", "Crawfor",
        "Edwards", "Gilbert", "Greens", "GrnHill", "IDOTRR", "Landmrk", "MeadowV",
        "Mitchel", "NAmes", "NoRidge", "NPkVill", "NridgHt", "NWAmes", "OldTown",
        "Sawyer", "SawyerW", "Somerst", "StoneBr", "SWISU", "Timber", "Veenker"
    ] | None = "CollgCr"
    Condition1: Literal["Artery", "Feedr", "Norm", "PosA", "PosN", "RRAe", "RRAn", "RRNe", "RRNn"] | None = "Norm"
    Condition2: Literal["Artery", "Feedr", "Norm", "PosA", "PosN", "RRAe", "RRAn", "RRNe", "RRNn"] | None = "Norm"
    BldgType: Literal["1Fam", "2fmCon", "Duplex", "Twnhs", "TwnhsE"] | None = "1Fam"
    HouseStyle: Literal["1.5Fin", "1.5Unf", "1Story", "2.5Fin", "2.5Unf", "2Story", "SFoyer", "SLvl"] | None = "2Story"
    OverallQual: int | None = Field(7, ge=1, le=10)
    OverallCond: int | None = Field(5, ge=1, le=10)
    YearBuilt: int | None = Field(2003, ge=1800, le=2100)
    YearRemodAdd: int | None = Field(2003, ge=1800, le=2100)
    RoofStyle: Literal["Flat", "Gable", "Gambrel", "Hip", "Mansard", "Shed"] | None = "Gable"
    RoofMatl: Literal["ClyTile", "CompShg", "Membran", "Metal", "Roll", "Tar&Grv", "WdShake", "WdShngl"] | None = "CompShg"
    Exterior1st: Literal[
        "AsbShng", "AsphShn", "BrkComm", "BrkFace", "CBlock", "CemntBd", "HdBoard",
        "ImStucc", "MetalSd", "Other", "Plywood", "PreCast", "Stone", "Stucco",
        "VinylSd", "Wd Sdng", "WdShing"
    ] | None = "VinylSd"
    Exterior2nd: Literal[
        "AsbShng", "AsphShn", "BrkComm", "BrkFace", "CBlock", "CemntBd", "HdBoard",
        "ImStucc", "MetalSd", "Other", "Plywood", "PreCast", "Stone", "Stucco",
        "VinylSd", "Wd Sdng", "WdShing"
    ] | None = "VinylSd"
    MasVnrType: Literal["BrkCmn", "BrkFace", "CBlock", "None", "Stone"] | None = "BrkFace"
    MasVnrArea: float | None = Field(196.0, ge=0)
    ExterQual: Literal["Ex", "Fa", "Gd", "TA"] | None = "Gd"
    ExterCond: Literal["Ex", "Fa", "Gd", "Po", "TA"] | None = "TA"
    Foundation: Literal["BrkTil", "CBlock", "PConc", "Slab", "Stone", "Wood"] | None = "PConc"
    BsmtQual: Literal["Ex", "Fa", "Gd", "TA", "NA"] | None = "Gd"
    BsmtCond: Literal["Ex", "Fa", "Gd", "Po", "TA", "NA"] | None = "TA"
    BsmtExposure: Literal["Av", "Gd", "Mn", "No", "NA"] | None = "No"
    BsmtFinType1: Literal["ALQ", "BLQ", "GLQ", "LwQ", "Rec", "Unf", "NA"] | None = "GLQ"
    BsmtFinSF1: int | None = Field(706, ge=0)
    BsmtFinType2: Literal["ALQ", "BLQ", "GLQ", "LwQ", "Rec", "Unf", "NA"] | None = "Unf"
    BsmtFinSF2: int | None = Field(0, ge=0)
    BsmtUnfSF: int | None = Field(150, ge=0)
    TotalBsmtSF: int | None = Field(856, ge=0)
    Heating: Literal["Floor", "GasA", "GasW", "Grav", "OthW", "Wall"] | None = "GasA"
    HeatingQC: Literal["Ex", "Fa", "Gd", "Po", "TA"] | None = "Ex"
    CentralAir: Literal["N", "Y"] | None = "Y"
    Electrical: Literal["FuseA", "FuseF", "FuseP", "Mix", "SBrkr"] | None = "SBrkr"
    FstFlrSF: int | None = Field(856, ge=0)
    SndFlrSF: int | None = Field(854, ge=0)
    LowQualFinSF: int | None = Field(0, ge=0)
    GrLivArea: int | None = Field(1710, ge=0)
    BsmtFullBath: int | None = Field(1, ge=0)
    BsmtHalfBath: int | None = Field(0, ge=0)
    FullBath: int | None = Field(2, ge=0)
    HalfBath: int | None = Field(1, ge=0)
    BedroomAbvGr: int | None = Field(3, ge=0)
    KitchenAbvGr: int | None = Field(1, ge=0)
    KitchenQual: Literal["Ex", "Fa", "Gd", "TA"] | None = "Gd"
    TotRmsAbvGrd: int | None = Field(8, ge=0)
    Functional: Literal["Maj1", "Maj2", "Min1", "Min2", "Mod", "Sev", "Typ"] | None = "Typ"
    Fireplaces: int | None = Field(0, ge=0)
    FireplaceQu: Literal["Ex", "Fa", "Gd", "Po", "TA", "NA", "nan"] | None = "nan"
    GarageType: Literal["2Types", "Attchd", "Basment", "BuiltIn", "CarPort", "Detchd", "NA"] | None = "Attchd"
    GarageYrBlt: float | None = Field(2003.0, ge=1800, le=2100)
    GarageFinish: Literal["Fin", "RFn", "Unf", "NA"] | None = "RFn"
    GarageCars: int | None = Field(2, ge=0, le=5)
    GarageArea: int | None = Field(548, ge=0)
    GarageQual: Literal["Ex", "Fa", "Gd", "Po", "TA", "NA"] | None = "TA"
    GarageCond: Literal["Ex", "Fa", "Gd", "Po", "TA", "NA"] | None = "TA"
    PavedDrive: Literal["N", "P", "Y"] | None = "Y"
    WoodDeckSF: int | None = Field(0, ge=0)
    OpenPorchSF: int | None = Field(61, ge=0)
    EnclosedPorch: int | None = Field(0, ge=0)
    ThirdSsnPorch: int | None = Field(0, ge=0)
    ScreenPorch: int | None = Field(0, ge=0)
    PoolArea: int | None = Field(0, ge=0)
    PoolQC: Literal["Ex", "Fa", "Gd", "NA", "nan"] | None = "nan"
    Fence: Literal["GdPrv", "GdWo", "MnPrv", "MnWw", "NA", "nan"] | None = "nan"
    MiscFeature: Literal["Gar2", "Othr", "Shed", "TenC", "NA", "nan"] | None = "nan"
    MiscVal: int | None = Field(0, ge=0)
    MoSold: int | None = Field(2, ge=1, le=12)
    YrSold: int | None = Field(2008, ge=2000, le=2100)
    SaleType: Literal["CWD", "Con", "ConLD", "ConLI", "ConLw", "New", "Oth", "WD"] | None = "WD"
    SaleCondition: Literal["Abnorml", "AdjLand", "Alloca", "Family", "Normal", "Partial"] | None = "Normal"    


class Prediction(BaseModel):
    #model_config = {"protected_namespaces": ()}

    predicted_price: float | None
    model_version: str
    request_id: str
    latency_ms: float
    status_code: int

class BatchPrediction(BaseModel):
    batch_id: str
    total_items: int
    batch_latency_ms: float
    results: list[Prediction]


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


@app.exception_handler(RequestValidationError)
async def custom_validation_handler(request: Request, exc: RequestValidationError):
    
    request_id = str(uuid.uuid4())
    status_code = 422
    price = None
    payload = None
    
    try:
        db.save_prediction(
            request_id=request_id,
            features=payload,
            price=price,
            model_version=app.state.version,
            latency_ms=0,
            answer_code=status_code
        )
    except Exception:
        pass
    
    return PlainTextResponse('', status_code=422)



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

        #raise Exception()

        bg.add_task(db.save_prediction, request_id, payload, price, app.state.version, latency_ms, status_code)

        return Prediction(predicted_price=price, model_version=app.state.version, request_id=request_id, latency_ms=latency_ms, status_code=status_code)
            
  
    except Exception:
        status_code = 500
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        bg.add_task(db.save_prediction, request_id, payload, price, app.state.version, latency_ms, status_code)

        raise HTTPException(status_code=500, detail="Internal error") from None


@app.post("/v1/predict/batch")
def predict_batch(items: list[Features], bg: BackgroundTasks) -> BatchPrediction:
    
    t0 = time.perf_counter()
    batch_id = str(uuid.uuid4())
    status_code = 200
    results = []
    
    try:
        payloads = [x.model_dump() for x in items]
        frame = pd.DataFrame(payloads).reindex(columns=app.state.meta["features"])

        predictions = app.state.pipeline.predict(frame)

        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
  
        for i, pred_value in enumerate(predictions):
            row_request_id = str(uuid.uuid4())
            row_payload = payloads[i]
            row_price = float(pred_value)
            results.append(Prediction(
                    predicted_price=row_price,
                    model_version=app.state.version,
                    request_id=row_request_id,
                    latency_ms=latency_ms,
                    status_code=200
                    )
                )
            bg.add_task(db.save_prediction, row_request_id, row_payload, row_price, app.state.version, latency_ms, status_code)

        return BatchPrediction(
                    batch_id=batch_id,
                    total_items=len(items),
                    batch_latency_ms=latency_ms,
                    results=results
                )

    except Exception:
        status_code = 500
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)

        bg.add_task(db.save_prediction, row_request_id, None, None, app.state.version, latency_ms, status_code)

        raise HTTPException(status_code=500, detail="Internal error") from None




