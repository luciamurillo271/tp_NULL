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
nacidos_22 = pd.read_csv(carpeta_originales+"nacweb22_0.csv")

establecimientos_de_salud = pd.read_excel(carpeta_originales+"establecimientos-asistenciales-asentados-registro-federal-refes-20220404.xlsx")

censo_10 = pd.read_excel(carpeta_originales+"censo2010.xlsx", skiprows=15)
censo_22 = pd.read_excel(carpeta_originales+"censo2022.xlsx", skiprows=15)


#%%-----------------------------------------------------------------------------------------
# LIMPIEZA DE DATOS CENTROS DE SALUD

#de centros de salud seleccionamos solo las columnas: id_establecimiento, nombre_establecimiento, id_provincia, id_depto, tipologia_nombre, origen_financiamiento
 
centro_de_salud = establecimientos_de_salud[["establecimiento_id", "establecimiento_nombre", "provincia_id", "departamento_id", "tipologia_nombre", "origen_financiamiento"]].copy()

#preguntitas random
print(centro_de_salud.head(5))
print(centro_de_salud["establecimiento_id"].is_unique) # TRUE
print(centro_de_salud.isna().sum()) #0
print(centro_de_salud.duplicated().sum()) #0
print(centro_de_salud["tipologia_nombre"].value_counts(dropna=False))

#para ver como agrupar el financiamiento en estatal o privado
#problema de calidad!!! catgoria 'Otros' podria contener origenes mezclados,
# y 'Mixta' no entra en ninguna, entre las dos suman 206, un 0,6% del total de centros de salud,
#no representativo
print(centro_de_salud["origen_financiamiento"].value_counts(dropna=False))


#Definimos las categorías
privados = ["Privado", "Obra social", "Universitario privado", "Mutual"]
estatales = ["Provincial", "Municipal", "FFAA/Seguridad", "Nacional", "Servicio Penitenciario Provincial", "Universitario público", "Servicio Penitenciario Federal"]

# Valor por default mixto/otro, y cambiamos el resto con la copia de la original
columna_original = centro_de_salud["origen_financiamiento"]
centro_de_salud["origen_financiamiento"] = "Otro/Mixto"
centro_de_salud.loc[columna_original.isin(privados), "origen_financiamiento"] = "Privado"
centro_de_salud.loc[columna_original.isin(estatales), "origen_financiamiento"] = "Estatal"

#preguntitas
print(centro_de_salud["origen_financiamiento"].value_counts(dropna=False)) # no se escapó ninguna
print(centro_de_salud.head(25))


# TERMINA LIMPIEZA DE CENTROS DE SALUD --------------------------------------------
centro_de_salud.to_csv(carpeta_modelo + "centro_de_salud.csv", index=False)



#%%-------------------------------------------------------------------------------------------
#LIMPIEZA DE DATOS NACIDOS VIVOS

#columnas que queremos con los nombres que queremos
nacidos_10 = nacidos_10[["IMEDAD", "PROVRES", "IMINSTRUC", "TIPPARTO", "ITIEMGEST", "IPESONAC", "CUENTA"]].copy()
nacidos_10["año"] = 2010
nacidos_10 = nacidos_10.rename(columns={
    "IMEDAD" : "rango_edad_madre",
    "PROVRES" : "id_provincia",
    "IMINSTRUC": "nivel_instruccion_madre",
    "TIPPARTO": "tipo_parto",
    "ITIEMGEST": "tipo_gestacion",
    "IPESONAC": "peso_hijo",
    "CUENTA": "cantidad"
    })
#queremos sacar el numero antes del rango etario, str split parte el texto en el punto, tomamos la segunda parte
nacidos_10["rango_edad_madre"] = nacidos_10["rango_edad_madre"].str.split(".", n=1).str[1]


#algunas preguntas
print(nacidos_10.shape)
print(nacidos_10.dtypes)
print(nacidos_10.isna().sum()) # no hay nulls explicitos
print(nacidos_10["rango_edad_madre"].value_counts(dropna=False).sort_index())
#%%---------------------------------------------------------------------------------------------
#LIMPIEZA DE DATOS CENSOS



#%%-----------------------------------------------------------------------------------------------
#creamos tabla provincia a partir de datos de establecimientos de salud

provincia = """
                SELECT DISTINCT "provincia_id" AS id, "provincia_nombre" AS nombre
                FROM establecimientos_de_salud
                ORDER BY id
                
            """
provincia = dd.sql(provincia).df()


#PROBLEMA CON NOMBRE DE ID INCORRECTO
"""
86                CHACO
86  SANTIAGO DEL ESTERO
62              CHUBUT
62            RÍO NEGRO
66                SALTA
66              CÓRDOBA
"""
pares_incorrectos = [(50, "SAN LUIS"), (58, "RÍO NEGRO"), (62, "CHUBUT"), (66, "CÓRDOBA"), (86, "CHACO")]
for id_provincia, nombre_provincia in pares_incorrectos:
    provincia = provincia[~((provincia["id"] == id_provincia) & (provincia["nombre"] == nombre_provincia))]

provincia = provincia.reset_index(drop=True)
    

provincia.to_csv(carpeta_modelo + "provincia.csv", index=False)


#%%---------------------------------------------------------------------------------------------
# BOCETO CONSULTA ii)
consulta = """
                SELECT p.nombre, cs.origen_financiamiento, COUNT(*) AS cant_con_terapia_intensiva, 
                FROM centro_de_salud AS cs
                JOIN provincia AS p
                ON cs.provincia_id = p.id
                WHERE tipologia_nombre LIKE '%terapia intensiva%'
                GROUP BY p.nombre, cs.origen_financiamiento
                ORDER BY p.nombre, cs.origen_financiamiento
            """
consulta_df = dd.sql(consulta).df()
print(consulta_df)


print(dd.sql("""
    SELECT COUNT(*) FROM centro_de_salud
    WHERE tipologia_nombre LIKE '%terapia intensiva%'
""").df())
print(centro_de_salud.loc[centro_de_salud["tipologia_nombre"].str.contains("terapia intensiva"),
                          "tipologia_nombre"].value_counts())




