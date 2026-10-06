"""
 Acá va un enzabezado (ver consigna)
"""
import os
import pandas as pd
import duckdb as dd
import openpyxl as oxl

#%%---------------------

carpeta_principal = os.path.dirname(os.path.abspath(__file__)) + "/"
carpeta_originales = os.path.join(carpeta_principal, "TablasOriginales/")
carpeta_modelo = os.path.join(carpeta_principal, "TablasModelo/")

nacidos_10 = pd.read_csv(carpeta_originales+"nacweb10.csv", encoding="latin-1")
nacidos_22 = pd.read_csv(carpeta_originales+"nacweb22_0.csv", sep = ";")

establecimientos_de_salud = pd.read_excel(carpeta_originales+"establecimientos-asistenciales-asentados-registro-federal-refes-20220404.xlsx")

censo_10 = pd.read_excel(carpeta_originales+"censo2010.xlsx",header=None)
censo_22 = pd.read_excel(carpeta_originales+"censo2022.xlsx", header=None)

#%%-----------------------------------------------------------------------------------------
# LIMPIEZA DE DATOS CENTROS DE SALUD

#de centros de salud seleccionamos solo las columnas: id_establecimiento, nombre_establecimiento, id_provincia, id_depto, tipologia_nombre, origen_financiamiento
 
centro_de_salud = establecimientos_de_salud[["establecimiento_id", "establecimiento_nombre", "provincia_id", "departamento_id", "tipologia_nombre", "origen_financiamiento"]].copy()

#Definimos las categorías
privados = ["Privado", "Obra social", "Universitario privado", "Mutual"]
estatales = ["Provincial", "Municipal", "FFAA/Seguridad", "Nacional", "Servicio Penitenciario Provincial", "Universitario público", "Servicio Penitenciario Federal"]
otro_mixto = ["Otros", "Mixta"]

# Reemplazamos origen_financiamiento por las categorías definidas   
columna_original = centro_de_salud["origen_financiamiento"]
centro_de_salud.loc[columna_original.isin(privados), "origen_financiamiento"] = "Privado"
centro_de_salud.loc[columna_original.isin(estatales), "origen_financiamiento"] = "Estatal"
centro_de_salud.loc[columna_original.isin(otro_mixto), "origen_financiamiento"] = "Otro/Mixto"


# ARMAMOS CSV CENTRO DE SALUD --------------------------------------------
centro_de_salud.to_csv(carpeta_modelo + "centro_de_salud.csv", index=False)

#%%-------------------------------------------------------------------------------------------
#LIMPIEZA DE DATOS NACIDOS VIVOS 10

#columnas que queremos con los nombres que queremos
nacidos_10 = nacidos_10[["PROVRES", "IMEDAD", "IMINSTRUC", "ITIEMGEST", "IPESONAC", "CUENTA"]].copy()
nacidos_10["año"] = 2010
nacidos_10 = nacidos_10.rename(columns={
    "PROVRES" : "id_provincia",
    "IMEDAD" : "rango_edad_madre",
    "IMINSTRUC": "nivel_instruccion_madre",
    "ITIEMGEST": "tiempo_gestacion",
    "IPESONAC": "peso_bebe",
    "CUENTA": "cantidad"
    })

#queremos sacar el numero antes de la descripción, str split parte el texto en el punto, tomamos la segunda parte
columnas_con_codigo_y_descripcion = ["rango_edad_madre", "nivel_instruccion_madre", "tiempo_gestacion", "peso_bebe"]

for columna in columnas_con_codigo_y_descripcion:
    nacidos_10[columna] = nacidos_10[columna].str.split(".", n=1).str[1]


#borramos filas con "sin especificar"
columnas = nacidos_10.columns.tolist()
for col in columnas:
    nacidos_10[col] = nacidos_10[col].replace('Sin especificar', None)

nacidos_10 = nacidos_10.dropna()

#%%-----------------------------------------------------------------------------------------
#LIMPIEZA NACIDOS VIVOS 22
#columnas que queremos con los nombres que queremos
nacidos_22 = nacidos_22[["PROVRES", "IMEDAD", "IMINSTRUC", "ITIEMGEST", "IPESONAC", "CUENTA"]].copy()
nacidos_22["año"] = 2022
nacidos_22 = nacidos_22.rename(columns={
    "PROVRES" : "id_provincia",
    "IMEDAD" : "rango_edad_madre",
    "IMINSTRUC": "nivel_instruccion_madre",
    "ITIEMGEST": "tiempo_gestacion",
    "IPESONAC": "peso_bebe",
    "CUENTA": "cantidad"
    })

#queremos sacar el numero antes de la descripción, str split parte el texto en el punto, tomamos la segunda parte
columnas_con_codigo_y_descripcion = ["rango_edad_madre", "nivel_instruccion_madre", "tiempo_gestacion", "peso_bebe"]

for columna in columnas_con_codigo_y_descripcion:
    nacidos_22[columna] = nacidos_22[columna].str.split(".", n=1).str[1]

#borramos filas con "sin especificar"
columnas = nacidos_22.columns.tolist()
for col in columnas:
    nacidos_22[col] = nacidos_22[col].replace('Sin especificar', None)

nacidos_22 = nacidos_22.dropna()

#%%----------------------------------------------------------------------------------------------------
#JOIN TABLAS NACIDOS VIVOS
nacimientoSQL = """
    SELECT * 
    FROM nacidos_10, 
    UNION 
    SELECT * 
    FROM nacidos_22
    ORDER BY id_provincia, rango_edad_madre, año
"""
nacimientos = dd.sql(nacimientoSQL).df()
nacimientos = nacimientos[~nacimientos["id_provincia"].astype(str).isin(['98', '99'])]

#ARMAMOS EL CSV DE NACIMIENTO
nacimientos.to_csv(carpeta_modelo + "nacimiento.csv", index=False)