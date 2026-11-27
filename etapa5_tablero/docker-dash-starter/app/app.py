import dash
from dash import dcc  # dash core components
from dash import html # dash html components
from dash.dependencies import Input, Output, State
import requests
import json
from loguru import logger
import os
import math
from pathlib import Path

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app server
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# PREDICTION API URL
# Dirección de la API
api_url = os.getenv("API_URL", "127.0.0.1")
api_port = os.getenv("API_PORT", "8001")
api_url = "http://{}:{}/api/v1/predict".format(api_url, api_port)

# Leer la configuración del clasificador
ruta_config = (
    Path(__file__).resolve().parent
    / "configuracion_clasificacion.json"
)

with ruta_config.open(encoding="utf-8") as archivo:
    config_clasificacion = json.load(archivo)

# Estilos del tablero
COLOR_PRINCIPAL = "#FF5A5F"

estilo_tarjeta = {
    "backgroundColor": "white",
    "border": "1px solid #E8E8E8",
    "borderRadius": "16px",
    "padding": "25px",
    "boxShadow": "0 4px 15px rgba(0, 0, 0, 0.04)"
}

estilo_pendiente = {
    "backgroundColor": "#F7F8FA",
    "border": "1px dashed #D5D9E0",
    "borderRadius": "12px",
    "padding": "25px",
    "textAlign": "center",
    "color": "#717784"
}

# Campos numéricos del formulario de clasificación
campos_clasificacion = [
    ("Latitud", "clas_latitude", -90, 90, "any"),
    ("Longitud", "clas_longitude", -180, 180, "any"),
    ("Capacidad de huéspedes", "clas_accommodates", 1, None, 1),
    ("Habitaciones", "clas_bedrooms", 0, None, 1),
    ("Camas", "clas_beds", 0, None, 1),
    ("Baños", "clas_bathrooms", 0, None, 0.5),
    ("Mínimo de noches", "clas_minimum_nights", 1, None, 1),
    ("Cantidad total de amenidades", "clas_n_amenities", 0, None, 1),
    ("Precio por noche (USD)", "clas_price", 0.01, None, "any"),
    ("Años como anfitrión", "clas_host_years", 0, None, "any"),
    ("Cantidad de anuncios del anfitrión", "clas_host_listings", 1, None, 1),
    ("Número de reseñas", "clas_reviews", 5, None, 1),
    ("Reseñas por mes", "clas_reviews_month", 0, None, "any")
]

formulario_clasificacion = html.Div(
    [
        html.Div(
            [
                html.Label(
                    etiqueta,
                    htmlFor=identificador,
                    style={
                        "fontSize": "14px",
                        "fontWeight": "bold",
                        "marginBottom": "6px"
                    }
                ),
                dcc.Input(
                    id=identificador,
                    type="number",
                    min=minimo,
                    max=maximo,
                    step=paso,
                    placeholder="Ingresa un valor",
                    style={
                        "width": "100%",
                        "boxSizing": "border-box",
                        "marginBottom": "0"
                    }
                )
            ],
            style={
                "flex": "1 1 180px",
                "minWidth": "0"
            }
        )
        for etiqueta, identificador, minimo, maximo, paso
        in campos_clasificacion
    ],
    style={
        "display": "flex",
        "flexWrap": "wrap",
        "gap": "18px",
        "marginTop": "20px"
    }
)
# Opciones de sí/no para servicios y anfitrión
campos_si_no = [
    ("¿El baño es compartido?", "clas_shared_bath"),
    ("¿Tiene wifi?", "clas_wifi"),
    ("¿Tiene cocina?", "clas_kitchen"),
    ("¿Tiene parqueadero?", "clas_parking"),
    ("¿Tiene lavadora?", "clas_washer"),
    ("¿Tiene aire acondicionado?", "clas_air_conditioning"),
    ("¿Tiene espacio de trabajo?", "clas_workspace"),
    ("¿El anfitrión tiene identidad verificada?", "clas_host_verified")
]

servicios_clasificacion = html.Div(
    [
        html.Div(
            [
                html.Label(
                    etiqueta,
                    style={
                        "fontSize": "14px",
                        "fontWeight": "bold",
                        "marginBottom": "6px"
                    }
                ),
                dcc.Dropdown(
                    id=identificador,
                    options=[
                        {"label": "Sí", "value": 1},
                        {"label": "No", "value": 0}
                    ],
                    placeholder="Selecciona una opción",
                    clearable=False
                )
            ],
            style={
                "flex": "1 1 180px",
                "minWidth": "0"
            }
        )
        for etiqueta, identificador in campos_si_no
    ],
    style={
        "display": "flex",
        "flexWrap": "wrap",
        "gap": "18px",
        "marginTop": "25px"
    }
)
# Categorías utilizadas durante el entrenamiento
tipos_habitacion = [
    {"label": "Alojamiento entero", "value": "Entire home/apt"},
    {"label": "Habitación de hotel", "value": "Hotel room"},
    {"label": "Habitación privada", "value": "Private room"},
    {"label": "Habitación compartida", "value": "Shared room"}
]

tipos_propiedad = [
    {"label": "Condominio entero", "value": "Entire condo"},
    {"label": "Suite de huéspedes completa", "value": "Entire guest suite"},
    {"label": "Casa entera", "value": "Entire home"},
    {"label": "Apartamento entero", "value": "Entire rental unit"},
    {"label": "Otro", "value": "Other"},
    {"label": "Habitación privada en casa", "value": "Private room in home"},
    {
        "label": "Habitación privada en apartamento",
        "value": "Private room in rental unit"
    },
    {
        "label": "Habitación en hotel boutique",
        "value": "Room in boutique hotel"
    },
    {"label": "Habitación en hotel", "value": "Room in hotel"}
]

barrios = [
    "Bayview",
    "Bernal Heights",
    "Castro/Upper Market",
    "Chinatown",
    "Crocker Amazon",
    "Diamond Heights",
    "Downtown/Civic Center",
    "Excelsior",
    "Financial District",
    "Glen Park",
    "Golden Gate Park",
    "Haight Ashbury",
    "Inner Richmond",
    "Inner Sunset",
    "Lakeshore",
    "Marina",
    "Mission",
    "Nob Hill",
    "Noe Valley",
    "North Beach",
    "Ocean View",
    "Outer Mission",
    "Outer Richmond",
    "Outer Sunset",
    "Pacific Heights",
    "Parkside",
    "Potrero Hill",
    "Presidio",
    "Presidio Heights",
    "Russian Hill",
    "Seacliff",
    "South of Market",
    "Twin Peaks",
    "Visitacion Valley",
    "West of Twin Peaks",
    "Western Addition"
]

campos_categoricos = [
    (
        "Barrio",
        "clas_barrio",
        [{"label": barrio, "value": barrio} for barrio in barrios]
    ),
    ("Tipo de habitación", "clas_room_type", tipos_habitacion),
    ("Tipo de propiedad", "clas_property_type", tipos_propiedad)
]

categorias_clasificacion = html.Div(
    [
        html.Div(
            [
                html.Label(
                    etiqueta,
                    style={
                        "fontSize": "14px",
                        "fontWeight": "bold",
                        "marginBottom": "6px"
                    }
                ),
                dcc.Dropdown(
                    id=identificador,
                    options=opciones,
                    placeholder="Selecciona una opción",
                    clearable=False,
                    searchable=True
                )
            ],
            style={"marginBottom": "18px"}
        )
        for etiqueta, identificador, opciones in campos_categoricos
    ],
    style={"marginTop": "20px"}
)
# Layout del tablero
app.layout = html.Div(
    [
        # Encabezado
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "ANÁLISIS DE ALOJAMIENTOS",
                            style={
                                "fontSize": "12px",
                                "letterSpacing": "2px",
                                "fontWeight": "bold",
                                "marginBottom": "12px"
                            }
                        ),
                        html.H1(
                            "Airbnb en San Francisco",
                            style={
                                "fontSize": "40px",
                                "fontWeight": "bold",
                                "marginBottom": "15px"
                            }
                        ),
                        html.P(
                            "Explora el mercado y consulta los modelos "
                            "para apoyar tus decisiones como anfitrión.",
                            style={
                                "fontSize": "18px",
                                "maxWidth": "700px",
                                "marginBottom": "0"
                            }
                        )
                    ],
                    style={
                        "maxWidth": "1200px",
                        "margin": "0 auto"
                    }
                )
            ],
            style={
                "backgroundColor": COLOR_PRINCIPAL,
                "color": "white",
                "padding": "30px 30px"
            }
        ),

        # Contenido principal
        html.Div(
            [
                # Análisis exploratorio
                html.H2(
                    "Explora los alojamientos",
                    style={
                        "fontSize": "28px",
                        "fontWeight": "bold",
                        "marginBottom": "8px"
                    }
                ),
                html.P(
                    "Consulta las características de los alojamientos "
                    "y compara las opciones disponibles.",
                    style={
                        "color": "#687080",
                        "marginBottom": "25px"
                    }
                ),

                # Espacio para los filtros
                html.Div(
                    [
                        html.H4(
                            "Filtros de exploración",
                            style={
                                "fontSize": "18px",
                                "fontWeight": "bold"
                            }
                        ),
                        html.P(
                            "Los filtros se incorporarán junto con las "
                            "visualizaciones del análisis exploratorio.",
                            style={
                                "color": "#687080",
                                "marginBottom": "0"
                            }
                        )
                    ],
                    style={
                        **estilo_tarjeta,
                        "marginBottom": "25px"
                    }
                ),

                # Tres tarjetas para las visualizaciones
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    f"Visualización {numero}",
                                    style={
                                        "fontSize": "20px",
                                        "fontWeight": "bold"
                                    }
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Espacio para la gráfica",
                                            style={
                                                "fontWeight": "bold",
                                                "marginBottom": "8px"
                                            }
                                        ),
                                        html.P(
                                            "Pendiente de integrar "
                                            "los resultados del EDA.",
                                            style={"marginBottom": "0"}
                                        )
                                    ],
                                    style={
                                        **estilo_pendiente,
                                        "minHeight": "180px",
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "justifyContent": "center"
                                    }
                                )
                            ],
                            style={
                                **estilo_tarjeta,
                                "flex": "1 1 280px",
                                "minWidth": "0"
                            }
                        )
                        for numero in [1, 2, 3]
                    ],
                    style={
                        "display": "flex",
                        "flexWrap": "wrap",
                        "gap": "20px"
                    }
                ),

                # Modelos predictivos
                html.H2(
                    "Evalúa tu alojamiento",
                    style={
                        "fontSize": "28px",
                        "fontWeight": "bold",
                        "marginTop": "45px",
                        "marginBottom": "8px"
                    }
                ),
                html.P(
                    "Estima el precio por noche y consulta "
                    "la clasificación del alojamiento.",
                    style={
                        "color": "#687080",
                        "marginBottom": "25px"
                    }
                ),

                html.Div(
                    [
                        # Modelo de regresión
                        html.Div(
                            [
                                html.P(
                                    "MODELO DE REGRESIÓN",
                                    style={
                                        "color": COLOR_PRINCIPAL,
                                        "fontSize": "12px",
                                        "fontWeight": "bold",
                                        "letterSpacing": "1px"
                                    }
                                ),
                                html.H3(
                                    "Estima el precio por noche",
                                    style={
                                        "fontSize": "24px",
                                        "fontWeight": "bold"
                                    }
                                ),
                                html.P(
                                    "Consulta un precio estimado según "
                                    "las características del alojamiento.",
                                    style={"color": "#687080"}
                                ),
                                html.Div(
                                    "Aquí se incorporará el formulario "
                                    "del modelo de regresión.",
                                    style={
                                        **estilo_pendiente,
                                        "marginTop": "20px"
                                    }
                                ),
                                html.Div(
                                    "Estimación pendiente de integrar.",
                                    id="resultado_precio",
                                    style={
                                        "marginTop": "20px",
                                        "fontWeight": "bold"
                                    }
                                )
                            ],
                            style={
                                **estilo_tarjeta,
                                "flex": "1 1 380px",
                                "minWidth": "0"
                            }
                        ),

                        # Modelo de clasificación
                        html.Div(
                            [
                                html.P(
                                    "MODELO DE CLASIFICACIÓN",
                                    style={
                                        "color": COLOR_PRINCIPAL,
                                        "fontSize": "12px",
                                        "fontWeight": "bold",
                                        "letterSpacing": "1px"
                                    }
                                ),
                                html.H3(
                                    "Consulta la recomendación",
                                    style={
                                        "fontSize": "24px",
                                        "fontWeight": "bold"
                                    }
                                ),
                                html.P(
                                    "Consulta si el modelo clasifica "
                                    "el alojamiento como recomendado.",
                                    style={"color": "#687080"}
                                ),
                                categorias_clasificacion,
                                formulario_clasificacion,
                                servicios_clasificacion,
                                html.Button(
                                    "Consultar clasificación",
                                    id="boton_clasificacion",
                                    n_clicks=0,
                                    style={
                                        "backgroundColor": COLOR_PRINCIPAL,
                                        "color": "white",
                                        "border": "none",
                                        "borderRadius": "8px",
                                        "marginTop": "25px",
                                        "width": "100%",
                                        "cursor": "pointer"
                                    }
                                ),
                                html.Div(
                                    "Clasificación pendiente de conectar.",
                                    id="resultado_clasificacion",
                                    style={
                                        "marginTop": "20px",
                                        "fontWeight": "bold"
                                    }
                                ),
                                html.P(
                                    "La red neuronal se aplica a anuncios "
                                    "existentes con al menos cinco reseñas. "
                                    "La etiqueta «recomendado» corresponde "
                                    "a una calificación de 4,9 o más.",
                                    style={
                                        "fontSize": "13px",
                                        "color": "#687080",
                                        "marginTop": "20px",
                                        "marginBottom": "0"
                                    }
                                )
                            ],
                            style={
                                **estilo_tarjeta,
                                "flex": "1 1 380px",
                                "minWidth": "0"
                            }
                        )
                    ],
                    style={
                        "display": "flex",
                        "flexWrap": "wrap",
                        "gap": "20px",
                        "alignItems": "stretch"
                    }
                ),

                # Pie de página
                html.P(
                    "Proyecto ACTD · Universidad de los Andes "
                    "y Tecnológico de Monterrey",
                    style={
                        "textAlign": "center",
                        "color": "#687080",
                        "fontSize": "13px",
                        "marginTop": "40px",
                        "marginBottom": "0"
                    }
                )
            ],
            style={
                "maxWidth": "1200px",
                "margin": "0 auto",
                "padding": "35px 25px"
            }
        )
    ],
    style={
        "backgroundColor": "#F5F6F8",
        "minHeight": "100vh",
        "fontFamily": "Arial, sans-serif",
        "color": "#242936"
    }
)

# Identificadores de los campos, en el orden del formulario
ids_clasificacion = (
    [campo[1] for campo in campos_categoricos]
    + [campo[1] for campo in campos_clasificacion]
    + [campo[1] for campo in campos_si_no]
)


@app.callback(
    Output("resultado_clasificacion", "children"),
    Input("boton_clasificacion", "n_clicks"),
    [State(identificador, "value")
     for identificador in ids_clasificacion],
    prevent_initial_call=True
)
def consultar_clasificacion(n_clicks, *valores):
    datos = dict(zip(ids_clasificacion, valores))

    if any(valor is None for valor in valores):
        return "Completa todos los campos antes de consultar."

    # Revisar los valores numéricos
    for etiqueta, identificador, minimo, maximo, paso in campos_clasificacion:
        valor = datos[identificador]

        if not math.isfinite(valor):
            return f"Revisa el campo: {etiqueta}."

        if minimo is not None and valor < minimo:
            return f"{etiqueta}: el mínimo permitido es {minimo}."

        if maximo is not None and valor > maximo:
            return f"{etiqueta}: el máximo permitido es {maximo}."

        if paso == 1 and not float(valor).is_integer():
            return f"{etiqueta}: ingresa un número entero."

    # Inicializar las 67 variables
    alojamiento = {
        variable: 0.0
        for variable in config_clasificacion["variables"]
    }

    # Variables numéricas del formulario
    correspondencias = {
        "latitude": "clas_latitude",
        "longitude": "clas_longitude",
        "accommodates": "clas_accommodates",
        "bedrooms": "clas_bedrooms",
        "beds": "clas_beds",
        "bathrooms": "clas_bathrooms",
        "minimum_nights": "clas_minimum_nights",
        "n_amenities": "clas_n_amenities",
        "hosts_time_as_host_years": "clas_host_years",
        "host_listings_count": "clas_host_listings",
        "number_of_reviews": "clas_reviews",
        "reviews_per_month": "clas_reviews_month"
    }

    for variable, identificador in correspondencias.items():
        alojamiento[variable] = float(datos[identificador])

    # Misma transformación utilizada en la limpieza
    alojamiento["log_price"] = math.log(datos["clas_price"])

    # Servicios e identidad verificada
    indicadores = {
        "shared_bath": "clas_shared_bath",
        "wifi": "clas_wifi",
        "kitchen": "clas_kitchen",
        "parking": "clas_parking",
        "washer": "clas_washer",
        "air_conditioning": "clas_air_conditioning",
        "workspace": "clas_workspace",
        "host_identity_verified": "clas_host_verified"
    }

    for variable, identificador in indicadores.items():
        alojamiento[variable] = int(datos[identificador])

    # Convertir las categorías en variables dummy.
    # Las categorías de referencia conservan todos sus ceros.
    categorias = {
        "room_type": datos["clas_room_type"],
        "property_type": datos["clas_property_type"],
        "neighbourhood_cleansed": datos["clas_barrio"]
    }

    for prefijo, categoria in categorias.items():
        columna = f"{prefijo}_{categoria}"

        if columna in alojamiento:
            alojamiento[columna] = 1.0

    # Enviar la solicitud a la API
    try:
        respuesta = requests.post(
            api_url,
            json={"inputs": [alojamiento]},
            timeout=60
        )
    except requests.exceptions.RequestException:
        return (
            "No fue posible comunicarse con la API. "
            "Comprueba que esté ejecutándose en el puerto 8001."
        )

    if respuesta.status_code != 200:
        logger.error(
            f"Error de la API: {respuesta.status_code} "
            f"{respuesta.text}"
        )
        return (
            "La API no pudo procesar los datos. "
            "Revisa el mensaje en la terminal del tablero."
        )

    resultado = respuesta.json()
    clase = resultado["predictions"][0]

    etiqueta = "Recomendado" if clase == 1 else "No recomendado"

    return html.Div(
        [
            html.H4(
                etiqueta,
                style={
                    "color": "#167D57" if clase == 1 else "#9C4221",
                    "fontWeight": "bold"
                }
            ),
            html.P(
                "Clasificación estimada por la red neuronal "
                "con el umbral seleccionado en validación.",
                style={
                    "fontSize": "14px",
                    "fontWeight": "normal"
                }
            )
        ]
    )

if __name__ == '__main__':
    logger.info("Running dash")
    app.run(debug=True)
