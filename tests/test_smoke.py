def test_predict_smoke(client, good_row):
    r = client.post("/v1/predict", json=good_row)
    assert r.status_code == 200
    body = r.json()
    assert 0.0 <= body["predicted_price"]
    assert body["latency_ms"] >= 0
    assert body["model_version"]


def test_predict_handles_missing_total_charges(client, good_row):
    r = client.post("/v1/predict", json={**good_row, "Id": None})
    assert r.status_code == 200


def test_batch_and_single_agree(client, good_row):
    s1 = client.post("/v1/predict", json=good_row).json()["predicted_price"]
    s2 = client.post("/v1/predict", json=good_row).json()["predicted_price"]
    assert abs(s1 - s2) < 1e-12
