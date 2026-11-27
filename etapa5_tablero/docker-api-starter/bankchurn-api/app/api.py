import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from loguru import logger
from tensorflow import keras

from app import __version__, schemas
from app.config import settings

api_router = APIRouter()

# Ubicación del modelo y su configuración
carpeta_modelos = Path(__file__).resolve().parent / "modelos"

with open(
    carpeta_modelos / "configuracion_clasificacion.json",
    encoding="utf-8"
) as archivo:
    configuracion = json.load(archivo)

variables = configuracion["variables"]
nombres_keras = configuracion["nombres_keras"]
umbral = float(configuracion["umbral"])

# Cargar la red ya entrenada
modelo = keras.models.load_model(
    carpeta_modelos / "modelo_clasificacion.keras",
    compile=False
)

model_version = "etapa4b"


# Ruta para verificar que la API esté funcionando
@api_router.get(
    "/health",
    response_model=schemas.Health,
    status_code=200
)
def health() -> dict:
    health = schemas.Health(
        name=settings.PROJECT_NAME,
        api_version=__version__,
        model_version=model_version
    )

    return health.model_dump()


# Ruta para realizar las predicciones
@api_router.post(
    "/predict",
    response_model=schemas.PredictionResults,
    status_code=200
)
def predict(input_data: schemas.MultipleDataInputs) -> Any:

    if not input_data.inputs:
        raise HTTPException(
            status_code=400,
            detail="Debes enviar al menos un alojamiento."
        )

    # Verificar las variables de cada alojamiento
    for numero, alojamiento in enumerate(input_data.inputs, start=1):
        faltantes = sorted(set(variables) - set(alojamiento))
        adicionales = sorted(set(alojamiento) - set(variables))

        if faltantes or adicionales:
            raise HTTPException(
                status_code=400,
                detail={
                    "alojamiento": numero,
                    "variables_faltantes": faltantes,
                    "variables_adicionales": adicionales
                }
            )

    input_df = pd.DataFrame(input_data.inputs)[variables]

    if not np.isfinite(input_df.to_numpy(dtype=float)).all():
        raise HTTPException(
            status_code=400,
            detail="Las variables deben contener números finitos."
        )

    if (input_df["number_of_reviews"] < 5).any():
        raise HTTPException(
            status_code=400,
            detail=(
                "El modelo se aplica a alojamientos "
                "con al menos cinco reseñas."
            )
        )

    # Relacionar las columnas con los nombres de entrada de Keras
    entradas = {
        nombres_keras[variable]: (
            input_df[variable]
            .to_numpy(dtype="float32")
            .reshape(-1, 1)
        )
        for variable in variables
    }

    logger.info(f"Clasificando {len(input_df)} alojamiento(s)")

    probabilidades = modelo.predict(
        entradas,
        verbose=0
    ).ravel()

    predicciones = (probabilidades >= umbral).astype(int)

    return {
        "errors": None,
        "version": model_version,
        "predictions": predicciones.tolist(),
        "probabilities": probabilidades.tolist(),
        "umbral": umbral
    }
