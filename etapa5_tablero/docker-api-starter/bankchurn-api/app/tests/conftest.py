import json
import math
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


# Cliente de prueba, como en el taller
@pytest.fixture()
def client():
    with TestClient(app) as cliente:
        yield cliente


# Alojamiento real que ya probamos en la API y el tablero
@pytest.fixture()
def alojamiento():
    ruta = (
        Path(__file__).resolve().parents[1]
        / "modelos"
        / "configuracion_clasificacion.json"
    )

    with ruta.open(encoding="utf-8") as archivo:
        configuracion = json.load(archivo)

    datos = {
        variable: 0.0
        for variable in configuracion["variables"]
    }

    datos.update({
        "latitude": 37.76173,
        "longitude": -122.43604,
        "accommodates": 2,
        "bedrooms": 1,
        "beds": 2,
        "bathrooms": 1,
        "shared_bath": 0,
        "minimum_nights": 2,
        "n_amenities": 32,
        "wifi": 1,
        "kitchen": 1,
        "parking": 0,
        "washer": 1,
        "air_conditioning": 0,
        "workspace": 1,
        "room_type_Private room": 1,
        "property_type_Other": 1,
        "neighbourhood_cleansed_Castro/Upper Market": 1,
        "log_price": math.log(195.50),
        "host_identity_verified": 1,
        "hosts_time_as_host_years": 12,
        "host_listings_count": 1,
        "number_of_reviews": 154,
        "reviews_per_month": 1.93
    })

    return datos
