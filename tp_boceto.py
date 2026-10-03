"""
 Acá va un enzabezado (ver consigna)
"""

import pandas as pd
import duckdb as dd
import openpyxl as oxl

#%%---------------------
carpeta =  "/Users/emmav/OneDrive/Documents/Emma Tripaldi/FACU/SEGUNDO AÑO/LABO DE DATOS/TP 1/"



nacidos_10 = pd.read_csv(carpeta+"nacweb10.csv", encoding="latin-1")
nacidos_22 = pd.read_csv(carpeta+"nacweb22_0.csv")

establecimientos_de_salud = pd.read_excel(carpeta+"establecimientos-asistenciales-asentados-registro-federal-refes-20220404.xlsx")

censo_10 = pd.read_excel(carpeta+"censo2010.xlsx", skiprows=15)
censo_22 = pd.read_excel(carpeta+"censo2022.xlsx", skiprows=15)


#%%---------------------------
 #de centros de salud seleccionamos solo las columnas: id_establecimiento, nombre_establecimiento, tipologia_nombre, origen_financiamiento
 
centro_de_salud = establecimientos_de_salud[["establecimiento_id", "establecimiento_nombre", "provincia_id", "provincia_nombre", "departamento_id", "tipologia_nombre", "origen_financiamiento"]]

#preguntitas random
print(centro_de_salud.head(5))
print(centro_de_salud["establecimiento_id"].is_unique) # TRUE
print(centro_de_salud.isna().sum())
print(centro_de_salud.duplicated().sum())
print(centro_de_salud["tipologia_nombre"].value_counts(dropna=False))

# BOCETO CONSULTA ii)
consulta = """
                SELECT provincia_nombre, origen_financiamiento, COUNT(*) AS cant_con_terapia_intensiva, 
                FROM centro_de_salud
                WHERE tipologia_nombre LIKE '%terapia intensiva%'
                GROUP BY provincia_nombre, origen_financiamiento
            """
consulta_df = dd.sql(consulta).df()
print(consulta_df)






