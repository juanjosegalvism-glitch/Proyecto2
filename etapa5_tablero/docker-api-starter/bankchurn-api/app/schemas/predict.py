from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# Esquema de los resultados de predicción
class PredictionResults(BaseModel):
    errors: Optional[Any] = None
    version: str
    predictions: List[int]
    probabilities: List[float]
    umbral: float


# Esquema para recibir uno o varios alojamientos
class MultipleDataInputs(BaseModel):
    inputs: List[Dict[str, float]]
