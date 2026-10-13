# Журнал ошибок
1. Первый запуск - сдох на тестах - ruff все не понравилось 
2. Сломался на этапе билда - не поменял имя базы 
3. забыл добавить секреты, поэтому база не инициализировалась
4. смок тест завалился из-за неправильного формата good.json (хотя вообще странно что смок тесты локально до этого норально отрабатывали)
5. почему то не создалась таблица - ссылка неправильная

# 2.1. 
1. Интеграционные тесты
```
def test_prediction_is_logged(client, good_row):
    body = client.post("/v1/predict", json=good_row).json()

    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute(
            "SELECT model_version, predicted_price, latency_ms, answer_code " 
            "FROM predictions WHERE request_id = %s",
            (body["request_id"],),
        ).fetchone()

    assert row is not None
    assert row[0] == body["model_version"]
    assert row[1] == pytest.approx(body["predicted_price"])
    assert row[-1] == 200

def test_prediction_422_is_logged(client, good_row):
    body = client.post("/v1/predict", json={}).json()

    with psycopg.connect(DATABASE_URL) as conn:
        row = conn.execute(
            "SELECT model_version, predicted_price, latency_ms, answer_code " 
            "FROM predictions WHERE request_id = %s",
            (body["request_id"],),
        ).fetchone()

    assert row is not None
    assert row[-1] == 422
```

2. ConfigMap
Уровень логов

3. Свой Smoke
Проверка что предсказанаая цена больше или равна нулю.

https://github.com/coolkrya/ML_PRO2026/actions/runs/38293533274
ghcr.io/coolkrya/ml_pro2026:sha-3adec1bce36d8cd38c5c31bf58950ffde6de943c

# 2.2
https://github.com/coolkrya/ML_PRO2026/pull/11

# 2.3
1.
Сначала оставил ссылку только в configmap - тесты не собирались потому что во время их проведения configmap не используется
https://github.com/coolkrya/ML_PRO2026/actions/runs/38298337690
TypeError: expected str, bytes or os.PathLike object, not NoneType
Поотом оставил правильное значение в config.py чтобы пройти тесты. По итоггу поломка на деплое
https://github.com/coolkrya/ML_PRO2026/actions/runs/38298823065

<img width="1167" height="854" alt="image" src="https://github.com/user-attachments/assets/bafb45f2-dad1-4148-aa51-0fdf4f36e20b" />

Из логов можно понять что есть ошибка в пути.
фикс - https://github.com/coolkrya/ML_PRO2026/actions/runs/38299394700

2.
Поменял имя секрета
https://github.com/coolkrya/ML_PRO2026/actions/runs/38299891116
Не поднялась бд для который он используется

<img width="1202" height="94" alt="image" src="https://github.com/user-attachments/assets/50a534cc-c3aa-435c-81d7-c8a3e49da062" />

Из логов можно понять есть ошибка в secretRef, причем конкретно с именем
фикс - https://github.com/coolkrya/ML_PRO2026/actions/runs/38301667650

3.
resources:
	requests: {cpu: 100m, memory: 100000000Mi}
	limits: {memory: 200000000Mi}

<img width="771" height="221" alt="image" src="https://github.com/user-attachments/assets/3c183cec-1f81-452f-935b-e6c258f1b8bb" />

<img width="898" height="221" alt="image" src="https://github.com/user-attachments/assets/50cb1d0d-8b41-43b8-a036-018b6c93966f" />


красный прогон - https://github.com/coolkrya/ML_PRO2026/actions/runs/38302373073

зеленый прогон - https://github.com/coolkrya/ML_PRO2026/actions/runs/38324051446


# 3.
1. Сколько секунд шёл job build в первом прогоне и сколько во втором? Какой слой Dockerfile взят из кэша и почему именно он?

первый - 3 44

второй - 3 10

для повторного запуска для одной и той же версии без изменений

также при самой первой попытке сборки job build занимал 50 секунд, в последующих сборках ~20.
в большинстве случаев - когда окружение не меняется, а меняется лишь код сервиса то докер берет кеш слоев до момента копирования кода (на основе хешей слоев (текущих и предыдущих))
```
COPY src/ src/
RUN uv sync --frozen --no-dev
```
2. В логе deploy во время выката видны поды в ImagePullBackOff, а прогон при этом зелёный. Откуда эти поды и почему это не ошибка?

ImagePullBackOff - временное состояние пода, которое означает процесс подкачки образа перед его выкатом. Сама job напрямую не вледит за состояниями подов - она следит за доступностью и работоспособностью сервиса.

3. Какой путь проходит пароль базы от страницы настроек GitHub до переменной окружения в поде? Почему его нельзя положить в configmap.yaml?

GitHub во время ваполнения job подставляет реальное значение пароля в переменную `${{ secrets.DB_PASSWORD }}` (меняя или создавая обьект типа Secret). Configmap - открытый файл конфигурации системы (обьект типа configmap). Для подобной цели как раз и существуют обьекты типа secret.  

4. Уберите мысленно needs: tests у job build. Опишите сценарий, в котором это закончится плохо.

Тесты проверяют функциональные требования к коду, которые можно проверить до сборки образа. При этом если мы уберем tests перед сборкой и деплоем, эти  этапы могут пройти бесшовно (если в них нету встроенных функциональных тестов (например тот же самый smoke)) и что создаст иллюзию отличного результата.

5. Почему на pull request у вас бегут только тесты, а build и deploy нет? Какая строка за это отвечает и зачем так сделано?

за это отвечают строки
```
on:

push: {branches: [main]}
pull_request:
```
Запускать билд и деплой при каждом пул реквесте наверное слишком затратно - ветка может быть не важной, или неактуальной. При этом это всегда можно поменять в зависимости от специфики репозитория.

6. Зачем в init() стоит pg_advisory_xact_lock? Что произойдёт без него при двух репликах и пустой базе? Реплики чего именно здесь имеются в виду?

pg_advisory_xact_lock - блокировка на уровне транзакции.
Две реплики сервиса обращаются к одной бд и выполняют один и тот же инициализирующий запрос по созданию таблицы. Если транзакции не заблокировать есть шанс словить взаимную блокировку. 

7. В трёх ваших красных прогонах поды застряли в трёх разных статусах. Расположите эти статусы в порядке жизни пода и объясните, на каком шаге возникает каждый.

configmap - умер на этапе теста - без правильного путя до модели функциональные требования не могут быть выполнены
secrets - deploy - бд не поднялась
requests - deploy - бд не поднялась тк в postgres.yaml ресурсы выходили за логичные ограничения.


