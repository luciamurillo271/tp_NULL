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
    ROUND(h10.con_cobertura*100.0/h10.total_habitantes, 2) AS porcentaje_con_cobertura_en_2010, 
    ROUND(h10.sin_cobertura*100.0/h10.total_habitantes, 2) AS porcentaje_sin_cobertura_en_2010, 
    ROUND(h22.con_cobertura*100.0/h22.total_habitantes, 2) AS porcentaje_con_cobertura_en_2022, 
    ROUND(h22.sin_cobertura*100.0/h22.total_habitantes, 2) AS porcentaje_sin_cobertura_en_2022
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
    SELECT provincia_id, COUNT(*) AS cant_privados,
    FROM centro_de_salud
    WHERE origen_financiamiento = 'Privado'
    GROUP BY provincia_id
"""
establecimientos_privados = dd.sql(establecimientos_privadosSQL).df()

establecimientos_estatalesSQL = """
    SELECT provincia_id, COUNT(*) AS cant_estatales,
    FROM centro_de_salud
    WHERE origen_financiamiento = 'Estatal'
    GROUP BY provincia_id
"""
establecimientos_estatales = dd.sql(establecimientos_estatalesSQL).df()

establecimientos_totalesSQL = """
    SELECT provincia_id, COUNT(*) AS cant_total_establecimientos,
    FROM centro_de_salud
    GROUP BY provincia_id
"""
establecimientos_totales = dd.sql(establecimientos_totalesSQL).df()

establecimientos_por_provincia_SQL = """
                SELECT p.nombre AS provincia, 
                ep.cant_privados AS cantidad_establecimientos_privados, 
                ee.cant_estatales AS cantidad_establecimientos_estatales,
                et.cant_total_establecimientos
                FROM establecimientos_privados AS ep
                JOIN establecimientos_estatales AS ee
                ON ep.provincia_id = ee.provincia_id
                JOIN establecimientos_totales AS et
                ON ep.provincia_id = et.provincia_id
                JOIN provincia AS p
                ON ep.provincia_id = p.id
                GROUP BY p.nombre, cantidad_establecimientos_privados, cantidad_establecimientos_estatales, cant_total_establecimientos
                ORDER BY p.nombre
            """
establecimientos_por_provincia = dd.sql(establecimientos_por_provincia_SQL).df()

establecimientos_por_provincia.to_csv(
    os.path.join(carpeta_analisis, "Establecimientos_de_salud_por_provincia.csv"),
    index=False)

#%%------------------------------------------------------------------------------------
edad_fertil = ['15 a 19', '20 a 24', '25 a 29', '30 a 34', '35 a 39', '40 a 44', '45 a 49']

mujeres_2010_SQL = """
    SELECT id_provincia, grupo_etario, SUM(cantidad) AS cant_mujeres
    FROM habitante
    WHERE anio = 2010 AND grupo_etario IN ('15 a 19', '20 a 24', '25 a 29', '30 a 34', '35 a 39', '40 a 44', '45 a 49') AND sexo = 'mujer'
    GROUP BY id_provincia, grupo_etario
"""
mujeres_2010 = dd.sql(mujeres_2010_SQL).df()

nacidos_2010_SQL = """
    SELECT id_provincia, grupo_etario_madre AS grupo_etario, SUM(cantidad) AS cant_nacidos
    FROM nacimiento
    WHERE anio = 2010
    GROUP BY id_provincia, grupo_etario

"""
nacidos_2010 = dd.sql(nacidos_2010_SQL).df()

tasa_fecundidad_2010_SQL = """
    SELECT p.nombre AS provincia, m.grupo_etario, 
    ROUND(n.cant_nacidos/m.cant_mujeres*1000, 2) AS tasa_fecundidad
    FROM mujeres_2010 AS m
    JOIN nacidos_2010 AS n
    ON m.id_provincia = n.id_provincia AND m.grupo_etario = n.grupo_etario
    JOIN provincia AS p
    ON p.id = m.id_provincia 
    ORDER BY p.nombre, m.grupo_etario
"""
tasa_fecundidad_2010 = dd.sql(tasa_fecundidad_2010_SQL).df()

tasa_fecundidad_2010.to_csv(
    os.path.join(carpeta_analisis, "Tasa_fecundidad_2010.csv"),
    index=False)

#%%-------------------------------------------------------------------------------------
#CONSULTA 5
porcentaje_madres_menores_2022_SQL = """
    WITH cantidades_22 AS (
        SELECT id_provincia, SUM(cantidad) AS total_nacidos, 
        SUM(CASE WHEN grupo_etario_madre IN ('Menor de 15','15 a 19') THEN cantidad ELSE 0 END) AS cant_madres_menores_20
        FROM nacimiento 
        WHERE anio = 2022
        GROUP BY id_provincia
    )
    SELECT id_provincia, ROUND(cant_madres_menores_20*100.0/total_nacidos, 2) AS porcentaje_madres_menores_2022
    FROM cantidades_22
    ORDER BY id_provincia
"""
porcentaje_madres_menores_2022 = dd.sql(porcentaje_madres_menores_2022_SQL).df()

porcentaje_madres_menores_2010_SQL = """
    WITH cantidades_10 AS (
        SELECT id_provincia, SUM(cantidad) AS total_nacidos, 
        SUM(CASE WHEN grupo_etario_madre IN ('Menor de 15','15 a 19') THEN cantidad ELSE 0 END) AS cant_madres_menores_20
        FROM nacimiento 
        WHERE anio = 2010
        GROUP BY id_provincia
    )
    SELECT id_provincia, ROUND(cant_madres_menores_20*100.0/total_nacidos, 2) AS porcentaje_madres_menores_2010
    FROM cantidades_10
    ORDER BY id_provincia
"""
porcentaje_madres_menores_2010 = dd.sql(porcentaje_madres_menores_2010_SQL).df()

cambios_edad_madresSQL = """
    SELECT p.nombre AS provincia, p10.porcentaje_madres_menores_2010, p22.porcentaje_madres_menores_2022, (p10.porcentaje_madres_menores_2010 - p22.porcentaje_madres_menores_2022) AS diferencia_porcetaje
    FROM porcentaje_madres_menores_2022 AS p22
    JOIN porcentaje_madres_menores_2010 AS p10
    ON p22.id_provincia = p10.id_provincia
    JOIN provincia AS p
    ON p.id = p22.id_provincia
    GROUP BY p.nombre, p10.porcentaje_madres_menores_2010, p22.porcentaje_madres_menores_2022
    ORDER BY diferencia_porcetaje DESC
"""
cambios_edad_madres = dd.sql(cambios_edad_madresSQL).df()

cambios_edad_madres.to_csv(
    os.path.join(carpeta_analisis, "Cambios_en_la_edad_de_las_madres_con_porcentajes.csv"), index=False)

#%%------------------------------------------------------------------------------
#PASAR LAS CONSULTAS NUEVAS A EXCEL
porc_habitantes_con_sin_cobertura.to_excel(
    os.path.join(carpeta_analisis, "Cobertura_de_salud_porcentaje.xlsx"),
    index=False)

establecimientos_por_provincia.to_excel(
    os.path.os.path.join(carpeta_analisis, "Establecimientos_de_salud_por_provincia.xlsx"),
    index=False)

tasa_fecundidad_2010.to_excel(
    os.path.join(carpeta_analisis, "Tasa_fecundidad_2010.xlsx"),
    index=False)

cambios_edad_madres.to_excel(
    os.path.join(carpeta_analisis, "Cambios_en_la_edad_de_las_madres_con_porcentajes.xlsx"), 
    index=False)