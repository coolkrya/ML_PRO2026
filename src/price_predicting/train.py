"""Обучение модели предсказания цены: проверка данных, обучение, запись в MLflow, регистрация и гейт.

  MLFLOW_TRACKING_URI=http://127.0.0.1:5000 uv run python -m price.train

Новая версия всегда получает алиас challenger. Алиас champion она получает, только если
R2 на отложенной выборке лучше, чем у текущего champion (или champion ещё нет).
"""
import json
import os
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd
import sklearn
from mlflow import MlflowClient
from mlflow.exceptions import MlflowException
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, TargetEncoder

DATA_PATH = Path(os.getenv("DATA_PATH", "datasets/house_prices.csv"))
MODEL_NAME = os.getenv("MODEL_NAME", "house_price")
EXPERIMENT = os.getenv("MLFLOW_EXPERIMENT", "house_price")
LEARNING_RATE = float(os.getenv("LEARNING_RATE", "0.1"))
MIN_GAIN = float(os.getenv("GATE_MIN_GAIN", "0.01"))  
SEED = 42

SKOPS_TRUSTED = [
    "numpy.dtype",
    "sklearn.compose._column_transformer._RemainderColsList",
    "sklearn.ensemble._gb.GradientBoostingRegressor",
    "sklearn.preprocessing._target_encoder.TargetEncoder",
    "sklearn.tree._tree.Tree"
]

CATEGORICAL = [
    "MSZoning", "Street", "Alley", "LotShape", "LandContour", "Utilities",
    "LotConfig", "LandSlope", "Neighborhood", "Condition1", "Condition2",
    "BldgType", "HouseStyle", "RoofStyle", "RoofMatl", "Exterior1st",
    "Exterior2nd", "MasVnrType", "ExterQual", "ExterCond", "Foundation",
    "BsmtQual", "BsmtCond", "BsmtExposure", "BsmtFinType1", "BsmtFinType2",
    "Heating", "HeatingQC", "CentralAir", "Electrical", "KitchenQual",
    "Functional", "FireplaceQu", "GarageType", "GarageFinish", "GarageQual",
    "GarageCond", "PavedDrive", "PoolQC", "Fence", "MiscFeature", "SaleType",
    "SaleCondition",
]

QUANTITATIVE = [
    "MSSubClass", "LotFrontage", "LotArea", "OverallQual", "OverallCond",
    "YearBuilt", "YearRemodAdd", "MasVnrArea", "BsmtFinSF1", "BsmtFinSF2",
    "BsmtUnfSF", "TotalBsmtSF", "FstFlrSF", "SndFlrSF", "LowQualFinSF",
    "GrLivArea", "BsmtFullBath", "BsmtHalfBath", "FullBath", "HalfBath",
    "BedroomAbvGr", "KitchenAbvGr", "TotRmsAbvGrd", "Fireplaces", "GarageYrBlt",
    "GarageCars", "GarageArea", "WoodDeckSF", "OpenPorchSF", "EnclosedPorch",
    "ThirdSsnPorch", "ScreenPorch", "PoolArea", "MiscVal", "MoSold", "YrSold",
]


numeric_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ("target_enc", TargetEncoder(target_type="continuous", smooth="auto"))
])

preprocessor = ColumnTransformer(
    transformers=[
        ("num", numeric_transformer, QUANTITATIVE),
        ("cat", categorical_transformer, CATEGORICAL),
    ],
    remainder="drop",
)


def load_and_validate(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    
    required_cols = QUANTITATIVE + CATEGORICAL + ["SalePrice"]
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(f"в данных нет колонок: {sorted(missing)}")
    
    if len(df) < 1000:
        raise ValueError(f"слишком мало строк: {len(df)}")
    
    # Таргет не должен содержать NaN 
    df = df.dropna(subset=["SalePrice"])
    df["SalePrice"] = pd.to_numeric(df["SalePrice"], errors="coerce")
    df = df.dropna(subset=["SalePrice"])
    
    if (df["SalePrice"] <= 0).any():
        raise ValueError("цена дома (SalePrice) должна быть строго больше 0")
        
    return df


def build_pipeline(learning_rate: float) -> Pipeline:
    return Pipeline([
        ("preprocessing", preprocessor),
        ("model", GradientBoostingRegressor(
            learning_rate=learning_rate, 
            random_state=SEED,
            n_estimators=10  
        ))
    ])


def champion_r2(client: MlflowClient) -> tuple[str | None, float | None]:
    """Возвращает версию и R2 текущего чемпиона."""
    try:
        mv = client.get_model_version_by_alias(MODEL_NAME, "champion")
    except MlflowException:
        return None, None
    
    run = client.get_run(mv.run_id)
    
    return mv.version, run.data.metrics.get("r2")


def main() -> dict:
    df = load_and_validate(DATA_PATH)
    features = QUANTITATIVE + CATEGORICAL
    
    
    x_train, x_test, y_train, y_test = train_test_split(
        df[features], df["SalePrice"], test_size=0.2, random_state=SEED
    )

    pipeline = build_pipeline(LEARNING_RATE).fit(x_train, y_train)
    preds = pipeline.predict(x_test)
    
    rmse = float(np.sqrt(mean_squared_error(y_test, preds)))
    r2 = float(r2_score(y_test, preds))

    mlflow.set_experiment(EXPERIMENT)
    client = MlflowClient()
    
    with mlflow.start_run() as run:
        metadata = {
            "features": features,
            "n_train": len(x_train),
            "data_rows": len(df),
            "sklearn": sklearn.__version__
        }
        
        mlflow.log_params({
            "learning_rate": LEARNING_RATE,
            "model": "GradientBoostingRegressor",
            "seed": SEED,
            "data": str(DATA_PATH)
        })
        
        mlflow.log_metrics({"rmse": rmse, "r2": r2})
        mlflow.log_dict(metadata, "metadata.json")
        
        info = mlflow.sklearn.log_model(
            pipeline, 
            name="model", 
            registered_model_name=MODEL_NAME,
            skops_trusted_types=SKOPS_TRUSTED
        )
        version = info.registered_model_version

    old_version, old_r2 = champion_r2(client)
    
  
    promoted = old_r2 is None or r2 > old_r2 + MIN_GAIN
    
    client.set_registered_model_alias(MODEL_NAME, "challenger", version)
    if promoted:
        client.set_registered_model_alias(MODEL_NAME, "champion", version)

    result = {
        "run_id": run.info.run_id,
        "version": version,
        "rmse": round(rmse, 2),
        "r2": round(r2, 4),
        "champion_before": old_version,
        "champion_r2_before": round(old_r2, 4) if old_r2 is not None else None,
        "promoted": promoted
    }
    
    print(json.dumps(result, ensure_ascii=False))
  
    xcom = Path("/airflow/xcom")
    if xcom.is_dir():
        (xcom / "return.json").write_text(json.dumps(result))
        
    return result


if __name__ == "__main__":
    main()