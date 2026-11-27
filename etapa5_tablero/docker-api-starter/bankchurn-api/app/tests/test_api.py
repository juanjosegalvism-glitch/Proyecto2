import math


def test_health(client):
    respuesta = client.get("/api/v1/health")

    assert respuesta.status_code == 200
    assert respuesta.json()["name"] == "Airbnb San Francisco API"
    assert respuesta.json()["model_version"] == "etapa4b"


def test_prediccion_alojamiento_real(client, alojamiento):
    respuesta = client.post(
        "/api/v1/predict",
        json={"inputs": [alojamiento]}
    )

    assert respuesta.status_code == 200

    resultado = respuesta.json()

    assert resultado["errors"] is None
    assert resultado["predictions"] == [1]
    assert resultado["umbral"] == 0.3
    assert len(resultado["probabilities"]) == 1

    # Comparar con la salida obtenida en la prueba manual
    assert math.isclose(
        resultado["probabilities"][0],
        0.6882966756820679,
        rel_tol=0.0001,
        abs_tol=0.00001
    )


def test_rechazar_variable_faltante(client, alojamiento):
    alojamiento.pop("latitude")

    respuesta = client.post(
        "/api/v1/predict",
        json={"inputs": [alojamiento]}
    )

    assert respuesta.status_code == 400
    assert "latitude" in (
        respuesta.json()["detail"]["variables_faltantes"]
    )


def test_rechazar_menos_de_cinco_resenas(client, alojamiento):
    alojamiento["number_of_reviews"] = 4

    respuesta = client.post(
        "/api/v1/predict",
        json={"inputs": [alojamiento]}
    )

    assert respuesta.status_code == 400
    assert "cinco reseñas" in respuesta.json()["detail"]
