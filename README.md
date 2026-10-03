
## Запуск и тесты


### Pytest

```
uv sync

uv run pytest

# ожидаемый результат 8 passed 1 skipped
```

###  Docker compose
```
docker compose up -d --build

docker ps

curl -X 'POST' \
  'http://localhost:8000/v1/predict' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "Id": 0,
  "MSSubClass": 0,
  "MSZoning": "string",
  "LotFrontage": 0,
  "LotArea": 0,
  "Street": "string",
  "Alley": "string",
  "LotShape": "string",
  "LandContour": "string",
  "Utilities": "string",
  "LotConfig": "string",
  "LandSlope": "string",
  "Neighborhood": "string",
  "Condition1": "string",
  "Condition2": "string",
  "BldgType": "string",
  "HouseStyle": "string",
  "OverallQual": 0,
  "OverallCond": 0,
  "YearBuilt": 0,
  "YearRemodAdd": 0,
  "RoofStyle": "string",
  "RoofMatl": "string",
  "Exterior1st": "string",
  "Exterior2nd": "string",
  "MasVnrType": "string",
  "MasVnrArea": 0,
  "ExterQual": "string",
  "ExterCond": "string",
  "Foundation": "string",
  "BsmtQual": "string",
  "BsmtCond": "string",
  "BsmtExposure": "string",
  "BsmtFinType1": "string",
  "BsmtFinSF1": 0,
  "BsmtFinType2": "string",
  "BsmtFinSF2": 0,
  "BsmtUnfSF": 0,
  "TotalBsmtSF": 0,
  "Heating": "string",
  "HeatingQC": "string",
  "CentralAir": "string",
  "Electrical": "string",
  "FstFlrSF": 0,
  "SndFlrSF": 0,
  "LowQualFinSF": 0,
  "GrLivArea": 0,
  "BsmtFullBath": 0,
  "BsmtHalfBath": 0,
  "FullBath": 0,
  "HalfBath": 0,
  "BedroomAbvGr": 0,
  "KitchenAbvGr": 0,
  "KitchenQual": "string",
  "TotRmsAbvGrd": 0,
  "Functional": "string",
  "Fireplaces": 0,
  "FireplaceQu": "string",
  "GarageType": "string",
  "GarageYrBlt": 0,
  "GarageFinish": "string",
  "GarageCars": 0,
  "GarageArea": 0,
  "GarageQual": "string",
  "GarageCond": "string",
  "PavedDrive": "string",
  "WoodDeckSF": 0,
  "OpenPorchSF": 0,
  "EnclosedPorch": 0,
  "ThirdSsnPorch": 0,
  "ScreenPorch": 0,
  "PoolArea": 0,
  "PoolQC": "string",
  "Fence": "string",
  "MiscFeature": "string",
  "MiscVal": 0,
  "MoSold": 0,
  "YrSold": 0,
  "SaleType": "string",
  "SaleCondition": "string"
}'


docker exec -it ml_pro2026-db-1 psql -U postgres -d predictions -c "SELECT request_id, ts, predicted_price, latency_ms, answer_code FROM predictions"


wq

# ожидаемый ответ - вывод таблицы с нввой (единственной записью)
## вместо curl можно воспользоваться веб-мордой (http://localhost:8080/docs#/default/predict_v1_predict_post)

docker compose down -v

```

### Kubernetes
```
kind create cluster --name mlpro

docker build -t price-predicting-service:1.0 .

kind load docker-image price-predicting-service:1.0 --name mlpro

kubectl apply -f k8s/

kubectl get pods

kubectl port-forward svc/price-predicting-service 8080:80

# открыть второй терминал и там продублировать 3 шаг из Docker compose только с другим портом

curl -X 'POST' \
  'http://localhost:8080/v1/predict' \
  -H 'accept: */*' \
  -H 'Content-Type: application/json' \
  -d '{
  "Id": 0,
  "MSSubClass": 0,
  "MSZoning": "string",
  "LotFrontage": 0,
  "LotArea": 0,
  "Street": "string",
  "Alley": "string",
  "LotShape": "string",
  "LandContour": "string",
  "Utilities": "string",
  "LotConfig": "string",
  "LandSlope": "string",
  "Neighborhood": "string",
  "Condition1": "string",
  "Condition2": "string",
  "BldgType": "string",
  "HouseStyle": "string",
  "OverallQual": 0,
  "OverallCond": 0,
  "YearBuilt": 0,
  "YearRemodAdd": 0,
  "RoofStyle": "string",
  "RoofMatl": "string",
  "Exterior1st": "string",
  "Exterior2nd": "string",
  "MasVnrType": "string",
  "MasVnrArea": 0,
  "ExterQual": "string",
  "ExterCond": "string",
  "Foundation": "string",
  "BsmtQual": "string",
  "BsmtCond": "string",
  "BsmtExposure": "string",
  "BsmtFinType1": "string",
  "BsmtFinSF1": 0,
  "BsmtFinType2": "string",
  "BsmtFinSF2": 0,
  "BsmtUnfSF": 0,
  "TotalBsmtSF": 0,
  "Heating": "string",
  "HeatingQC": "string",
  "CentralAir": "string",
  "Electrical": "string",
  "FstFlrSF": 0,
  "SndFlrSF": 0,
  "LowQualFinSF": 0,
  "GrLivArea": 0,
  "BsmtFullBath": 0,
  "BsmtHalfBath": 0,
  "FullBath": 0,
  "HalfBath": 0,
  "BedroomAbvGr": 0,
  "KitchenAbvGr": 0,
  "KitchenQual": "string",
  "TotRmsAbvGrd": 0,
  "Functional": "string",
  "Fireplaces": 0,
  "FireplaceQu": "string",
  "GarageType": "string",
  "GarageYrBlt": 0,
  "GarageFinish": "string",
  "GarageCars": 0,
  "GarageArea": 0,
  "GarageQual": "string",
  "GarageCond": "string",
  "PavedDrive": "string",
  "WoodDeckSF": 0,
  "OpenPorchSF": 0,
  "EnclosedPorch": 0,
  "ThirdSsnPorch": 0,
  "ScreenPorch": 0,
  "PoolArea": 0,
  "PoolQC": "string",
  "Fence": "string",
  "MiscFeature": "string",
  "MiscVal": 0,
  "MoSold": 0,
  "YrSold": 0,
  "SaleType": "string",
  "SaleCondition": "string"
}'

k9s

# на одной из нод должен появится лог о POST-зопросе
```




## Док-ва
### 1. Pytest
1 skipped, т.к. бд не поднимается отдельно, а пихать pytest внутрь контейнера для полноценного теста абсурд. Для Dockerfile url для бд раскомменчивается.
<img width="1285" height="637" alt="image" src="https://github.com/user-attachments/assets/97eaf7c2-c080-4084-83f4-cbc85bcdf5de" />

Колхозный вариант - сделать проверку с помощью докерного адреса контейнера с бд, который будет поднят "позже".
<img width="1202" height="405" alt="image" src="https://github.com/user-attachments/assets/4275a879-ace9-4989-a4f9-0ac10a72647e" />

<img width="1290" height="897" alt="image" src="https://github.com/user-attachments/assets/6f56c91d-985d-41d1-ae29-f57e9bb1d727" />

<img width="852" height="297" alt="image" src="https://github.com/user-attachments/assets/c557dcd2-3c9f-4adb-84fe-6d501e71bae0" />


### 2. Select из логов
<img width="1280" height="916" alt="image" src="https://github.com/user-attachments/assets/34f90e48-2590-40eb-815b-c35c13af7b6e" />


### 3. Kubernetes
<img width="1281" height="832" alt="image" src="https://github.com/user-attachments/assets/13b1cf64-5e6f-4345-85f6-ccc55fae6364" />

Журнал проблем :
- Проблемы с окружениями - решения перезагрузки и пересборки
- Был казус с пересозданием схемы бд - забыл что том хранится на хостовой тачке


## Звездочки

# 1. Locust
Test 1
10 users, 5 ups, 60 sec
<img width="1274" height="385" alt="image" src="https://github.com/user-attachments/assets/4e7e47fe-bbf2-437c-ae81-67adf975764b" />

50 users, 10 ups, 60 sec
<img width="1268" height="438" alt="image" src="https://github.com/user-attachments/assets/43b66aa0-fc69-4195-9fdd-110f531bb24c" />

100 users, 20 ups, 60 sec
<img width="1288" height="480" alt="image" src="https://github.com/user-attachments/assets/38c477b3-2c3b-477e-91be-bf437a73c356" />

Вывод: значения p95 отличаются от медианного в среднем на одно и то же значение в течение всего тестирвоания. Единственный отрыв наблюдается в третьем эксперименте ближе к концу - причины непонятны. RPC не меняется, ошибки не выдает.

# 2. Batch tests
<img width="1268" height="884" alt="image" src="https://github.com/user-attachments/assets/4b6ca99a-84d6-44f9-b6d1-cffd2f9310a7" />

Тут слегка сложновато, потому что нету уверенности что все сделано правильно. Результаты из бд логов.

<img width="816" height="128" alt="image" src="https://github.com/user-attachments/assets/269bb14e-5e69-4323-843f-879c89574fb8" />

Данные что в locust, что в бд затрагивают и одиночные предсказания и предсказания по батчу.

Отдельно сравниваем в равных условиях среднюю задержку через бд.
Для одиночного предсказания.

<img width="518" height="105" alt="image" src="https://github.com/user-attachments/assets/19794716-a850-4e7b-8030-f5866efb32f8" />

Для батча.

<img width="517" height="124" alt="image" src="https://github.com/user-attachments/assets/f39145e4-4a06-40c1-a5a4-32e9ffcf4157" />

Результаты отличаются в 3 раза, а не 500 скорее всего из-за оптимизации numpy.

# 3. Выкат новой версии

<img width="499" height="73" alt="image" src="https://github.com/user-attachments/assets/1cd707b0-b148-4ec3-8de7-74fc2d3b7872" />

Сначала появляется под новой версии - один подов заменяется (постепенно заменяясь на новый Running -> Terminating), после все то же самое для второго. Почему вывод такой - все не с первого раза)

#
#
