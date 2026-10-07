"""
 Acá va un enzabezado (ver consigna)
"""
import os
import pandas as pd
import duckdb as dd

#%%---------------------
#LEEMOS LOS ARCHIVOS
carpeta_principal = os.path.dirname(os.path.abspath(__file__))
carpeta_originales = os.path.join(carpeta_principal, "TablasOriginales")
carpeta_modelo = os.path.join(carpeta_principal, "TablasModelo")
carpeta_consultas = os.path.join(carpeta_principal, "TablasConsultas")
carpeta_analisis = os.path.join(carpeta_principal, "TablasAnalisis")

nacidos_10 = pd.read_csv(
    os.path.join(carpeta_originales, "nacweb10.csv"),
    encoding="latin-1"
)
nacidos_22 = pd.read_csv(
    os.path.join(carpeta_originales, "nacweb22_0.csv"),
    encoding="utf-8-sig",
    sep=";"
)

establecimientos_de_salud = pd.read_excel(
    os.path.join(
        carpeta_originales,
        "establecimientos-asistenciales-asentados-registro-federal-refes-20220404.xlsx"
    )
)

censo_10 = pd.read_excel(
    os.path.join(carpeta_originales, "censo2010.xlsx"),
    header=None
)
censo_22 = pd.read_excel(
    os.path.join(carpeta_originales, "censo2022.xlsx"),
    header=None
)

#LEEMOS NUESTRAS TABLAS
nacimiento = pd.read_csv(os.path.join(carpeta_modelo, "nacimiento.csv"))
provincia = pd.read_csv(os.path.join(carpeta_modelo, "provincia.csv"))
centro_de_salud = pd.read_csv(os.path.join(carpeta_modelo, "centro_de_salud.csv"))
departamento = pd.read_csv(os.path.join(carpeta_modelo, "departamento.csv"))
habitante = pd.read_csv(os.path.join(carpeta_modelo, "habitante.csv"))

#LEEMOS LAS TABLAS DE CONSULTAS
establecimientos_con_terapia_intensiva = pd.read_csv(os.path.join(carpeta_consultas, "Establecimientos_de_salud_con_terapia_intensiva.csv"))
caracteristicas_nacimientos = pd.read_csv(os.path.join(carpeta_consultas, "Caracteristicas_de_los_nacimientos.csv"))
tasa_fecundidad_2022 = pd.read_csv(os.path.join(carpeta_consultas, "Tasa_fecundidad_2022.csv"))
cambios_edad_madres = pd.read_csv(os.path.join(carpeta_consultas, "Cambios_en_la_edad_de_las_madres.csv"))
cobertura_de_salud = pd.read_csv(os.path.join(carpeta_consultas, "Cobertura_de_salud.csv"))

#%%-------------------------------------------------------------------------------------
#CONSULTAS PARA ANALISIS
#CONSULTA 1
cant_habitantes_con_sin_cober_2010_SQL = """
    SELECT id_provincia, grupo_etario, 
    SUM(CASE WHEN anio = 2010 AND cobertura = 'Tiene' THEN cantidad ELSE 0 END) AS con_cobertura,
    SUM(CASE WHEN anio = 2010 AND cobertura = 'No tiene' THEN cantidad ELSE 0 END) AS sin_cobertura,
    SUM(CASE WHEN anio = 2010 THEN cantidad ELSE 0 END) AS total_habitantes
    FROM habitante
    GROUP BY id_provincia, grupo_etario
"""
cant_habitantes_con_sin_cober_2010 = dd.sql(cant_habitantes_con_sin_cober_2010_SQL).df()

cant_habitantes_con_sin_cober_2022_SQL = """
    SELECT id_provincia, grupo_etario, 
    SUM(CASE WHEN anio = 2022 AND cobertura = 'Tiene' THEN cantidad ELSE 0 END) AS con_cobertura,
    SUM(CASE WHEN anio = 2022 AND cobertura = 'No tiene' THEN cantidad ELSE 0 END) AS sin_cobertura,
    SUM(CASE WHEN anio = 2022 THEN cantidad ELSE 0 END) AS total_habitantes
    FROM habitante
    GROUP BY id_provincia, grupo_etario
"""
cant_habitantes_con_sin_cober_2022 = dd.sql(cant_habitantes_con_sin_cober_2022_SQL).df()


porc_habitantes_con_sin_cobertura_SQL = """
    SELECT p.nombre AS provincia, h10.grupo_etario AS grupo_etario, 
    (h10.con_cobertura*100.0/h10.total_habitantes) AS porcentaje_con_cobertura_en_2010, 
    (h10.sin_cobertura*100.0/h10.total_habitantes) AS porcentaje_sin_cobertura_en_2010, 
    (h22.con_cobertura*100.0/h22.total_habitantes) AS porcentaje_con_cobertura_en_2022, 
    (h22.sin_cobertura*100.0/h22.total_habitantes) AS porcentaje_sin_cobertura_en_2022
    FROM cant_habitantes_con_sin_cober_2010 AS h10
    JOIN cant_habitantes_con_sin_cober_2022 AS h22
    ON h10.grupo_etario = h22.grupo_etario AND h10.id_provincia = h22.id_provincia
    JOIN provincia AS p
    ON p.id = h10.id_provincia
    GROUP BY p.nombre, h10.grupo_etario, porcentaje_con_cobertura_en_2010, porcentaje_sin_cobertura_en_2010, porcentaje_con_cobertura_en_2022, porcentaje_sin_cobertura_en_2022
    ORDER BY p.nombre, CAST(split_part(h10.grupo_etario, ' ', 1) AS INTEGER)
"""
porc_habitantes_con_sin_cobertura = dd.sql(porc_habitantes_con_sin_cobertura_SQL).df()

porc_habitantes_con_sin_cobertura.to_csv(
    os.path.join(carpeta_analisis, "Cobertura_de_salud_porcentaje.csv"),
    index=False)

#%%-------------------------------------------------------------------------------
#CONSULTA 2
establecimientos_privadosSQL = """
    SELECT provincia_id, COUNT(*) AS cant_con_terapia_intensiva,
    FROM centro_de_salud
    WHERE tipologia_nombre LIKE '%terapia intensiva%' AND origen_financiamiento = 'Privado'
    GROUP BY provincia_id
"""
establecimientos_privados = dd.sql(establecimientos_privadosSQL).df()

establecimientos_estatalesSQL = """
    SELECT provincia_id, COUNT(*) AS cant_con_terapia_intensiva,
    FROM centro_de_salud
    WHERE tipologia_nombre LIKE '%terapia intensiva%' AND origen_financiamiento = 'Estatal'
    GROUP BY provincia_id
"""
establecimientos_estatales = dd.sql(establecimientos_estatalesSQL).df()

establecimientos_totalesSQL = """
    SELECT provincia_id, COUNT(*) AS cant_total_establecimientos,
    FROM centro_de_salud
    GROUP BY provincia_id
"""
establecimientos_totales = dd.sql(establecimientos_totalesSQL).df()

establecimientos_con_terapia_intensivaSQL = """
                SELECT p.nombre AS provincia, 
                ep.cant_con_terapia_intensiva AS cantidad_establecimientos_privados_con_intensiva, 
                ee.cant_con_terapia_intensiva AS cantidad_establecimientos_estatales_con_intensiva,
                et.cant_total_establecimientos
                FROM establecimientos_privados AS ep
                JOIN establecimientos_estatales AS ee
                ON ep.provincia_id = ee.provincia_id
                JOIN establecimientos_totales AS et
                ON ep.provincia_id = et.provincia_id
                JOIN provincia AS p
                ON ep.provincia_id = p.id
                GROUP BY p.nombre, cantidad_establecimientos_privados_con_intensiva, cantidad_establecimientos_estatales_con_intensiva, cant_total_establecimientos
                ORDER BY p.nombre
            """
establecimientos_por_provincia = dd.sql(establecimientos_con_terapia_intensivaSQL).df()

establecimientos_por_provincia.to_csv(
    os.path.join(carpeta_analisis, "Establecimientos_de_salud_por_provincia.csv"),
    index=False)


#%%------------------------------------------------------------------------------
#PASAR LAS CONSULTAS NUEVAS A EXCEL
porc_habitantes_con_sin_cobertura.to_excel(
    os.path.join(carpeta_analisis, "Cobertura_de_salud_porcentaje.xlsx"),
    index=False)

establecimientos_por_provincia.to_excel(
    os.path.os.path.join(carpeta_analisis, "Establecimientos_de_salud_por_provincia.xlsx"),
    index=False)