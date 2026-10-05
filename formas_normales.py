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

#%%-------------------------------------------------------------------------------------------------------
# localidad_id -> localidad_nombre
consulta1 = """
    SELECT localidad_id,
           COUNT(DISTINCT localidad_nombre) AS cant_nombres
    FROM establecimientos_de_salud
    GROUP BY localidad_id
    HAVING COUNT(DISTINCT localidad_nombre) > 1
"""
q1 = dd.sql(consulta1).df()
print(q1)

# localidad_id -> provincia_id, departamento_id (¿hay una DF más?)
consulta2 = """
    SELECT localidad_id,
           COUNT(DISTINCT provincia_id) AS cant_prov,
           COUNT(DISTINCT departamento_id) AS cant_deptos
    FROM establecimientos_de_salud
    GROUP BY localidad_id
    HAVING COUNT(DISTINCT provincia_id) > 1
        OR COUNT(DISTINCT departamento_id) > 1
"""
q2 = dd.sql(consulta2).df()
print(q2)

# tipologia_id -> tipologia_sigla
consulta3 = """
    SELECT tipologia_id,
           COUNT(DISTINCT tipologia_sigla) AS cant_siglas
    FROM establecimientos_de_salud
    GROUP BY tipologia_id
    HAVING COUNT(DISTINCT tipologia_sigla) > 1
"""
q3 = dd.sql(consulta3).df()
print(q3)

# tipologia_id -> tipologia_nombre (para confirmar lo que viste: debería dar filas)
consulta4 = """
    SELECT tipologia_id,
           COUNT(DISTINCT tipologia_nombre) AS cant_nombres
    FROM establecimientos_de_salud
    GROUP BY tipologia_id
    HAVING COUNT(DISTINCT tipologia_nombre) > 1
"""
q4 = dd.sql(consulta4).df()
print(q4)

print(len(q1), len(q2), len(q3), len(q4))
