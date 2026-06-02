import os
import pandas as pd

DATA_PATH = "data/consumos.csv"

COLUMNAS = [
    "nombre_usuario",
    "correo_usuario",
    "anio",
    "bimestre",
    "consumo_kwh",
    "importe_total",
    "kwh_basico",
    "precio_basico",
    "kwh_intermedio",
    "precio_intermedio",
    "kwh_excedente",
    "precio_excedente"
]


def inicializar_csv():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=COLUMNAS)
        df.to_csv(DATA_PATH, index=False)


def guardar_registro(registro):
    inicializar_csv()

    df = pd.read_csv(DATA_PATH)
    nuevo = pd.DataFrame([registro])
    df = pd.concat([df, nuevo], ignore_index=True)

    df.to_csv(DATA_PATH, index=False)


def cargar_datos():
    inicializar_csv()
    return pd.read_csv(DATA_PATH)


def cargar_datos_usuario(correo_usuario):
    df = cargar_datos()

    if df.empty:
        return df

    return df[df["correo_usuario"] == correo_usuario].copy()

def eliminar_registro(indice):
    inicializar_csv()
    df = pd.read_csv(DATA_PATH)

    if indice in df.index:
        df = df.drop(index=indice)
        df.to_csv(DATA_PATH, index=False)


def actualizar_registro(indice, datos_actualizados):
    inicializar_csv()
    df = pd.read_csv(DATA_PATH)

    if indice in df.index:
        for columna, valor in datos_actualizados.items():
            df.loc[indice, columna] = valor

        df.to_csv(DATA_PATH, index=False)