from locust import HttpUser, task


class PredictUser(HttpUser):
    def payload(self):
        return  {
                "Id": 1,
                "MSSubClass": 60,
                "MSZoning": "RL",
                "LotFrontage": 65.0,
                "LotArea": 8450,
                "Street": "Pave",
                "Alley": "nan",
                "LotShape": "Reg",
                "LandContour": "Lvl",
                "Utilities": "AllPub",
                "LotConfig": "Inside",
                "LandSlope": "Gtl",
                "Neighborhood": "CollgCr",
                "Condition1": "Norm",
                "Condition2": "Norm",
                "BldgType": "1Fam",
                "HouseStyle": "2Story",
                "OverallQual": 7,
                "OverallCond": 5,
                "YearBuilt": 2003,
                "YearRemodAdd": 2003,
                "RoofStyle": "Gable",
                "RoofMatl": "CompShg",
                "Exterior1st": "VinylSd",
                "Exterior2nd": "VinylSd",
                "MasVnrType": "BrkFace",
                "MasVnrArea": 196.0,
                "ExterQual": "Gd",
                "ExterCond": "TA",
                "Foundation": "PConc",
                "BsmtQual": "Gd",
                "BsmtCond": "TA",
                "BsmtExposure": "No",
                "BsmtFinType1": "GLQ",
                "BsmtFinSF1": 706,
                "BsmtFinType2": "Unf",
                "BsmtFinSF2": 0,
                "BsmtUnfSF": 150,
                "TotalBsmtSF": 856,
                "Heating": "GasA",
                "HeatingQC": "Ex",
                "CentralAir": "Y",
                "Electrical": "SBrkr",
                "FstFlrSF": 856,
                "SndFlrSF": 854,
                "LowQualFinSF": 0,
                "GrLivArea": 1710,
                "BsmtFullBath": 1,
                "BsmtHalfBath": 0,
                "FullBath": 2,
                "HalfBath": 1,
                "BedroomAbvGr": 3,
                "KitchenAbvGr": 1,
                "KitchenQual": "Gd",
                "TotRmsAbvGrd": 8,
                "Functional": "Typ",
                "Fireplaces": 0,
                "FireplaceQu": "nan",
                "GarageType": "Attchd",
                "GarageYrBlt": 2003.0,
                "GarageFinish": "RFn",
                "GarageCars": 2,
                "GarageArea": 548,
                "GarageQual": "TA",
                "GarageCond": "TA",
                "PavedDrive": "Y",
                "WoodDeckSF": 0,
                "OpenPorchSF": 61,
                "EnclosedPorch": 0,
                "ThirdSsnPorch": 0,
                "ScreenPorch": 0,
                "PoolArea": 0,
                "PoolQC": "nan",
                "Fence": "nan",
                "MiscFeature": "nan",
                "MiscVal": 0,
                "MoSold": 2,
                "YrSold": 2008,
                "SaleType": "WD",
                "SaleCondition": "Normal"
            }
    
    
    @task(5)
    def test_predict(self):
        
        with self.client.post("/v1/predict", json=self.payload(), catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Predicting process failed {response.status_code}: {response.text}")

    @task(1)
    def test_health(self):
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed {response.status_code}: {response.text}")

    @task(5)
    def test_predict_batch(self):
        batch_payload = [self.payload() for _ in range(500)]
        
        with self.client.post("/v1/predict/batch", json=batch_payload, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed {response.status_code}: {response.text}")