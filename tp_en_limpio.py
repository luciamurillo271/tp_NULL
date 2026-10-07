"""
 Grupo: "NULL"
 Integralentes: Lucía Murillo, Victoria Florencia Lima, María Cecilia Marchesano y Emma Victoria Tripaldi
 Archivo del código del proceso de lectura y limpieza de los 5 archivos proporcionados por la materia,
 junto con la posterior importación de datos en nuestras 5 tablas: Nacimiento, Provincia, Departamento, 
 Habitante y Centro de salud. 
 Al final se encuentran las consultas y los gráficos producto de diferentes filtros que aplicamos a 
 estas tablas, para luego analizar sus resultados en el informe.
"""

#%%
import os
import pandas as pd
import duckdb as dd
import matplotlib.pyplot as plt 
import numpy as np

#%%-------------------------------------------------------------------------------------
#LEEMOS LOS ARCHIVOS
carpeta_principal = os.path.dirname(os.path.abspath(__file__))
carpeta_originales = os.path.join(carpeta_principal, "TablasOriginales")
carpeta_modelo = os.path.join(carpeta_principal, "TablasModelo")
carpeta_consultas = os.path.join(carpeta_principal, "TablasConsultas")

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


# ARMAMOS CSV CENTRO DE SALUD 
centro_de_salud.to_csv(
    os.path.join(carpeta_modelo, "centro_de_salud.csv"),
    index=False
)

#%%-------------------------------------------------------------------------------------------
#LIMPIEZA DE DATOS NACIDOS VIVOS 10

#columnas que queremos con los nombres que queremos
nacidos_10 = nacidos_10[["PROVRES", "IMEDAD", "IMINSTRUC", "ITIEMGEST", "IPESONAC", "CUENTA"]].copy()
nacidos_10["anio"] = 2010
nacidos_10 = nacidos_10.rename(columns={
    "PROVRES" : "id_provincia",
    "IMEDAD" : "grupo_etario_madre",
    "IMINSTRUC": "nivel_instruccion_madre",
    "ITIEMGEST": "tiempo_gestacion",
    "IPESONAC": "peso_bebe",
    "CUENTA": "cantidad"
    })

#queremos sacar el numero antes de la descripción, str split parte el texto en el punto, tomamos la segunda parte
columnas_con_codigo_y_descripcion = ["grupo_etario_madre", "nivel_instruccion_madre", "tiempo_gestacion", "peso_bebe"]

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
nacidos_22["anio"] = 2022
nacidos_22 = nacidos_22.rename(columns={
    "PROVRES" : "id_provincia",
    "IMEDAD" : "grupo_etario_madre",
    "IMINSTRUC": "nivel_instruccion_madre",
    "ITIEMGEST": "tiempo_gestacion",
    "IPESONAC": "peso_bebe",
    "CUENTA": "cantidad"
    })

#queremos sacar el numero antes de la descripción, str split parte el texto en el punto, tomamos la segunda parte
columnas_con_codigo_y_descripcion = ["grupo_etario_madre", "nivel_instruccion_madre", "tiempo_gestacion", "peso_bebe"]

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
    FROM nacidos_10 
    UNION 
    SELECT * 
    FROM nacidos_22
    ORDER BY id_provincia, grupo_etario_madre, anio
"""
nacimiento = dd.sql(nacimientoSQL).df()
nacimiento = nacimiento[~nacimiento["id_provincia"].astype(str).isin(['98', '99'])]

#ARMAMOS EL CSV DE NACIMIENTO
nacimiento.to_csv(
    os.path.join(carpeta_modelo, "nacimiento.csv"),
    index=False
)

#%%----------------------------------------------------------------------------------------------------
#LIMPIEZA DE DATOS CENSO 10

censo_10 = censo_10.iloc[:,1:6]
censo_10.columns = ["bloque", "edad","varon","mujer","total"]

#pasamos la columna bloques a una lista de todas las filas
areas_y_coberturas = censo_10["bloque"].fillna("").astype(str).str.strip().tolist()

area_actual = None           # el área que estamos recorriendo
cobertura_actual = None      # la cobertura que estamos recorriendo
texto_anterior = ""          # lo que decía la fila de arriba

lista_area = []
lista_cobertura = []
coberturas = ["Obra social (incluye PAMI)", "Prepaga a través de obra social", "Prepaga sólo por contratación voluntaria", "Programas o planes estatales de salud", "No tiene obra social, prepaga o plan estatal", "Total"]

#por cada fila de la columna "bloque" vamos guardando el área y la cobertura que corresponden
for texto in areas_y_coberturas:
    if texto.startswith("AREA #"): # Si la fila es un título de área, guardamos el código (sin "AREA # ")
        area_actual = texto.replace("AREA # ", "")
    elif texto in coberturas: # Si la fila es una cobertura, guardamos el texto
        cobertura_actual = texto
    elif texto == "RESUMEN":
        area_actual = None
        cobertura_actual = None

    lista_area.append(area_actual)
    lista_cobertura.append(cobertura_actual)

    texto_anterior = texto

#reemplazamos la columna "bloque" por la lista de áreas y la renombramos "id_provincia"
censo_10["bloque"] = lista_area
censo_10.rename(columns={"bloque":"id_provincia"}, inplace=True)
#agregamos la columna "cobertura" con la lista de coberturas (cada fila tiene la cobertura correspondiente)
censo_10["cobertura"] = lista_cobertura


sin_cobertura = ["No tiene obra social, prepaga o plan estatal"]
con_cobertura = ["Obra social (incluye PAMI)", "Prepaga a través de obra social", "Prepaga sólo por contratación voluntaria", "Programas o planes estatales de salud"]
totales = ["Total"]

# Reemplazamos los valores de la columna "cobertura" por "No tiene", "Tiene" o None según corresponda
censo_10.loc[censo_10["cobertura"].isin(sin_cobertura), "cobertura"] = "No tiene"
censo_10.loc[censo_10["cobertura"].isin(con_cobertura), "cobertura"] = "Tiene"
censo_10.loc[censo_10["cobertura"].isin(totales), "cobertura"] = None

censo_10 = censo_10.drop(columns=["total"])
censo_10 = censo_10.dropna()

#armamos una tabla con los varones y otra con las mujeres, renombramos la columna "varon" y "mujer" a "cantidad" y agregamos una columna "sexo" con el valor correspondiente
varones = censo_10[["id_provincia", "edad", "varon","cobertura"]].rename(columns={"varon":"cantidad"})
varones["sexo"] = "varon"

mujeres = censo_10[["id_provincia", "edad", "mujer","cobertura"]].rename(columns={"mujer":"cantidad"})
mujeres["sexo"] = "mujer"

#unimos las dos tablas en una sola
censo_10 = pd.concat([varones, mujeres], ignore_index=True)

#pasamos la columna edad a int
censo_10["edad"] = pd.to_numeric(censo_10["edad"], errors="coerce")
censo_10 = censo_10.dropna(subset=["edad"])
censo_10["edad"] = censo_10["edad"].astype(int)

#creamos columnas edad_inicio y edad_fin para agrupar en rangos etarios
censo_10["edad_inicio"] = (censo_10["edad"] // 5) * 5
censo_10["edad_fin"] = censo_10["edad_inicio"] + 4

#creamos la columna grupo_etario
censo_10["grupo_etario"] = (censo_10["edad_inicio"].astype(str) + " a " + censo_10["edad_fin"].astype(str))
censo_10.loc[censo_10["edad"] >= 100, "grupo_etario"] = "100 y más"

censo_10 = censo_10.drop(columns=["edad", "edad_inicio", "edad_fin"])
censo_10["anio"] = 2010


#%%-------------------------------------------------------------------------------------------
#LIMPIEZA CENSO 22
censo_22 = censo_22.iloc[:,1:6]
censo_22.columns = ["bloque", "edad","varon","mujer","total"]

#pasamos la columna bloques a una lista de todas las filas
areas_y_coberturas = censo_22["bloque"].fillna("").astype(str).str.strip().tolist()

area_actual = None           # el área que estamos recorriendo
cobertura_actual = None      # la cobertura que estamos recorriendo
texto_anterior = ""          # lo que decía la fila de arriba

lista_area = []
lista_cobertura = []
coberturas = ["Obra social o prepaga (incluye PAMI)", "Programas o planes estatales de salud", "No tiene obra social, prepaga ni plan estatal", "Total"]

#por cada fila de la columna "bloque" vamos guardando el área y la cobertura que corresponden
for texto in areas_y_coberturas:
    if texto.startswith("AREA #"): # Si la fila es un título de área, guardamos el código (sin "AREA # ")
        area_actual = texto.replace("AREA # ", "")
    elif texto in coberturas: # Si la fila es una cobertura, guardamos el texto
        cobertura_actual = texto
    elif texto == "RESUMEN":
        area_actual = None
        cobertura_actual = None

    lista_area.append(area_actual)
    lista_cobertura.append(cobertura_actual)

    texto_anterior = texto

#reemplazamos la columna "bloque" por la lista de áreas y la renombramos "id_provincia"
censo_22["bloque"] = lista_area
censo_22.rename(columns={"bloque":"id_provincia"}, inplace=True)
#agregamos la columna "cobertura" con la lista de coberturas (cada fila tiene la cobertura correspondiente)
censo_22["cobertura"] = lista_cobertura

sin_cobertura = ["No tiene obra social, prepaga ni plan estatal"]
con_cobertura = ["Obra social o prepaga (incluye PAMI)", "Programas o planes estatales de salud"]
totales = ["Total"]

# Reemplazamos los valores de la columna "cobertura" por "No tiene", "Tiene" o None según corresponda
censo_22.loc[censo_22["cobertura"].isin(sin_cobertura), "cobertura"] = "No tiene"
censo_22.loc[censo_22["cobertura"].isin(con_cobertura), "cobertura"] = "Tiene"
censo_22.loc[censo_22["cobertura"].isin(totales), "cobertura"] = None

censo_22 = censo_22.drop(columns=["total"])
censo_22 = censo_22.dropna()

#armamos una tabla con los varones y otra con las mujeres, renombramos la columna "varon" y "mujer" a "cantidad" y agregamos una columna "sexo" con el valor correspondiente
varones = censo_22[["id_provincia", "edad", "varon","cobertura"]].rename(columns={"varon":"cantidad"})
varones["sexo"] = "varon"

mujeres = censo_22[["id_provincia", "edad", "mujer","cobertura"]].rename(columns={"mujer":"cantidad"})
mujeres["sexo"] = "mujer"

#unimos las dos tablas en una sola
censo_22 = pd.concat([varones, mujeres], ignore_index=True)

#pasamos la columna edad a int
censo_22["edad"] = pd.to_numeric(censo_22["edad"], errors="coerce")
censo_22 = censo_22.dropna(subset=["edad"])
censo_22["edad"] = censo_22["edad"].astype(int)

#creamos columnas edad_inicio y edad_fin para agrupar en rangos etarios
censo_22["edad_inicio"] = (censo_22["edad"] // 5) * 5
censo_22["edad_fin"] = censo_22["edad_inicio"] + 4

#creamos la columna grupo_etario
censo_22["grupo_etario"] = (censo_22["edad_inicio"].astype(str) + " a " + censo_22["edad_fin"].astype(str))
censo_22.loc[censo_22["edad"] >= 100, "grupo_etario"] = "100 y más"

censo_22 = censo_22.drop(columns=["edad", "edad_inicio", "edad_fin"])
censo_22["anio"] = 2022


#%%------------------------------------------------------------------------------
# Unimos ambos censos

total_habitantesSQL = """
    SELECT * 
    FROM censo_10, 
    UNION 
    SELECT * 
    FROM censo_22
"""

total_habitantes = dd.sql(total_habitantesSQL).df()
total_habitantes["cantidad"] = pd.to_numeric(total_habitantes["cantidad"], errors="coerce")

# Agrupamos cantidades de misma provincia, sexo, cobertura, grupo etario y año
habitanteSQL = """
    SELECT id_provincia, SUM(cantidad) AS cantidad, cobertura, sexo, grupo_etario, anio
    FROM total_habitantes
    GROUP BY id_provincia, cobertura, sexo, grupo_etario, anio
    ORDER BY id_provincia, grupo_etario, anio
"""

habitante = dd.sql(habitanteSQL).df()

#ARMAMOS CSV HABITANTE
habitante.to_csv(
    os.path.join(carpeta_modelo, "habitante.csv"),
    index=False
)

#%%-----------------------------------------------------------------------------------------------
#creamos tabla PROVINCIA a partir de datos de establecimientos de salud

provinciaSQL = """
                SELECT DISTINCT "provincia_id" AS id, "provincia_nombre" AS nombre
                FROM establecimientos_de_salud
                ORDER BY id
                
            """
provincia = dd.sql(provinciaSQL).df()


#PROBLEMA CON NOMBRE DE ID INCORRECTO
"""
86                CHACO
86  SANTIAGO DEL ESTERO
62              CHUBUT
62            RÍO NEGRO
66                SALTA
66              CÓRDOBA
"""
#sacamos las filas con id y nombre incorrecto
pares_incorrectos = [(50, "SAN LUIS"), (58, "RÍO NEGRO"), (62, "CHUBUT"), (66, "CÓRDOBA"), (86, "CHACO")]
for id_provincia, nombre_provincia in pares_incorrectos:
    provincia = provincia[~((provincia["id"] == id_provincia) & (provincia["nombre"] == nombre_provincia))]

provincia = provincia.reset_index(drop=True)
    
# ARMAMOS CSV DE PROVINCIA
provincia.to_csv(
    os.path.join(carpeta_modelo, "provincia.csv"),
    index=False
)

#%%-----------------------------------------------------------------------------------------------
# Creamos tabla DEPARTAMENTO a partir de datos de establecimientos de salud
departamentoSQL = """
                SELECT DISTINCT "departamento_id" AS id, "departamento_nombre" AS nombre, "provincia_id" AS provincia_id
                FROM establecimientos_de_salud
                ORDER BY id
                
            """
departamento = dd.sql(departamentoSQL).df()

# ARMAMOS CSV DE DEPARTAMENTO
departamento.to_csv(
    os.path.join(carpeta_modelo, "departamento.csv"),
    index=False
)

#%%----------------------------------------------------------------------------------
#LEEMOS NUESTRAS TABLAS

nacimiento = pd.read_csv(os.path.join(carpeta_modelo, "nacimiento.csv"))
provincia = pd.read_csv(os.path.join(carpeta_modelo, "provincia.csv"))
centro_de_salud = pd.read_csv(os.path.join(carpeta_modelo, "centro_de_salud.csv"))
departamento = pd.read_csv(os.path.join(carpeta_modelo, "departamento.csv"))
habitante = pd.read_csv(os.path.join(carpeta_modelo, "habitante.csv"))

#%%--------------------------------------------------------------------------------------------
#CONSULTA 1: Cobertura de salud
cant_habitantes_con_sin_cober_2010_SQL = """
    SELECT id_provincia, grupo_etario, 
    SUM(CASE WHEN anio = 2010 AND cobertura = 'Tiene' THEN cantidad ELSE 0 END) AS con_cobertura,
    SUM(CASE WHEN anio = 2010 AND cobertura = 'No tiene' THEN cantidad ELSE 0 END) AS sin_cobertura
    FROM habitante
    GROUP BY id_provincia, grupo_etario
"""
cant_habitantes_con_sin_cober_2010 = dd.sql(cant_habitantes_con_sin_cober_2010_SQL).df()

cant_habitantes_con_sin_cober_2022_SQL = """
    SELECT id_provincia, grupo_etario, 
    SUM(CASE WHEN anio = 2022 AND cobertura = 'Tiene' THEN cantidad ELSE 0 END) AS con_cobertura,
    SUM(CASE WHEN anio = 2022 AND cobertura = 'No tiene' THEN cantidad ELSE 0 END) AS sin_cobertura
    FROM habitante
    GROUP BY id_provincia, grupo_etario
"""
cant_habitantes_con_sin_cober_2022 = dd.sql(cant_habitantes_con_sin_cober_2022_SQL).df()


cant_habitantes_con_sin_cobertura_SQL = """
    SELECT p.nombre AS provincia, h10.grupo_etario AS grupo_etario, 
    h10.con_cobertura AS Habitantes_con_cobertura_en_2010, 
    h10.sin_cobertura AS Habitantes_sin_cobertura_en_2010, 
    h22.con_cobertura AS Habitantes_con_cobertura_en_2022, 
    h22.sin_cobertura AS Habitantes_sin_cobertura_en_2022
    FROM cant_habitantes_con_sin_cober_2010 AS h10
    JOIN cant_habitantes_con_sin_cober_2022 AS h22
    ON h10.grupo_etario = h22.grupo_etario AND h10.id_provincia = h22.id_provincia
    JOIN provincia AS p
    ON p.id = h10.id_provincia
    GROUP BY p.nombre, h10.grupo_etario, Habitantes_con_cobertura_en_2010, Habitantes_sin_cobertura_en_2010, Habitantes_con_cobertura_en_2022, Habitantes_sin_cobertura_en_2022
    ORDER BY p.nombre, CAST(split_part(h10.grupo_etario, ' ', 1) AS INTEGER)
"""
cant_habitantes_con_sin_cobertura = dd.sql(cant_habitantes_con_sin_cobertura_SQL).df()

cant_habitantes_con_sin_cobertura.to_csv(
    os.path.join(carpeta_consultas, "Cobertura_de_salud.csv"),
    index=False)


#%%---------------------------------------------------------------------
#CONSULTA 2: Establecimientos de salud con terapia intensiva
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

establecimientos_con_terapia_intensivaSQL = """
                SELECT p.nombre AS provincia, ep.cant_con_terapia_intensiva AS cantidad_establecimientos_privados, ee.cant_con_terapia_intensiva AS cantidad_establecimientos_estatales
                FROM establecimientos_privados AS ep
                JOIN establecimientos_estatales AS ee
                ON ep.provincia_id = ee.provincia_id
                JOIN provincia AS p
                ON ep.provincia_id = p.id
                GROUP BY p.nombre, cantidad_establecimientos_privados, cantidad_establecimientos_estatales
                ORDER BY p.nombre
            """
establecimientos_con_terapia_intensiva = dd.sql(establecimientos_con_terapia_intensivaSQL).df()

establecimientos_con_terapia_intensiva.to_csv(
    os.path.join(carpeta_consultas, "Establecimientos_de_salud_con_terapia_intensiva.csv"),
    index=False)


#%%-----------------------------------------------------------------
#CONSULTA 3: Caracteristicas de los nacimientos
nacidos_por_provincia_y_edad_madre_2010SQL = """
    SELECT id_provincia, grupo_etario_madre, SUM(cantidad) AS cantidad_total
    FROM nacimiento
    WHERE anio = 2010
    GROUP BY id_provincia, grupo_etario_madre
    ORDER BY id_provincia, grupo_etario_madre
"""
nacidos_total_2010 = dd.sql(nacidos_por_provincia_y_edad_madre_2010SQL).df()
    
caracteristicas_2010_SQL = """
    SELECT t.id_provincia, t.grupo_etario_madre, t.cantidad_total, SUM(n.cantidad) AS cantidad_bajo_peso
    FROM nacimiento AS n
    JOIN nacidos_total_2010 as t
    ON t.id_provincia = n.id_provincia AND t.grupo_etario_madre = n.grupo_etario_madre
    WHERE n.peso_bebe = 'Menos de 2500 gramos' AND n.anio = 2010
    GROUP BY t.id_provincia, t.grupo_etario_madre, t.cantidad_total
"""
caracteristicas_2010 = dd.sql(caracteristicas_2010_SQL).df()

nacidos_por_provincia_y_edad_madre_2022SQL = """
    SELECT id_provincia, grupo_etario_madre, SUM(cantidad) AS cantidad_total
    FROM nacimiento
    WHERE anio = 2022
    GROUP BY id_provincia, grupo_etario_madre
    ORDER BY id_provincia, grupo_etario_madre
"""
nacidos_total_2022 = dd.sql(nacidos_por_provincia_y_edad_madre_2022SQL).df()
    
caracteristicas_2022_SQL = """
    SELECT t.id_provincia, t.grupo_etario_madre, t.cantidad_total, SUM(n.cantidad) AS cantidad_bajo_peso
    FROM nacimiento AS n
    JOIN nacidos_total_2022 as t
    ON t.id_provincia = n.id_provincia AND t.grupo_etario_madre = n.grupo_etario_madre
    WHERE n.peso_bebe = 'Menos de 2500 gramos' AND n.anio = 2022
    GROUP BY t.id_provincia, t.grupo_etario_madre, t.cantidad_total
"""
caracteristicas_2022 = dd.sql(caracteristicas_2022_SQL).df()

caracteristicas_nacimientos_SQL = """
    SELECT p.nombre, c10.grupo_etario_madre, c10.cantidad_total AS cantidad_nacimientos_2010, 
    ROUND(c10.cantidad_bajo_peso*100.0/c10.cantidad_total, 2) AS porcentaje_bajo_peso_2010,
    c22.cantidad_total AS cantidad_nacimientos_2022, 
    ROUND(c22.cantidad_bajo_peso*100.0/c22.cantidad_total, 2) AS porcentaje_bajo_peso_2022
    FROM caracteristicas_2010 AS c10
    JOIN caracteristicas_2022 AS c22
    ON c10.id_provincia = c22.id_provincia AND c10.grupo_etario_madre = c22.grupo_etario_madre
    JOIN provincia as p
    ON c10.id_provincia = p.id
    GROUP BY p.nombre, c10.grupo_etario_madre, cantidad_nacimientos_2010, porcentaje_bajo_peso_2010, cantidad_nacimientos_2022, porcentaje_bajo_peso_2022
    ORDER BY p.nombre ASC, CASE c10.grupo_etario_madre
            WHEN 'Menor de 15' THEN 1 WHEN '15 a 19' THEN 2 WHEN '20 a 24' THEN 3 
            WHEN '25 a 29' THEN 4 WHEN '30 a 34' THEN 5 WHEN '35 a 39' THEN 6 
            WHEN '40 a 44' THEN 7 WHEN 'De 45 y más' THEN 8
        END
"""
caracteristicas_nacimientos = dd.sql(caracteristicas_nacimientos_SQL).df()

caracteristicas_nacimientos.to_csv(
    os.path.join(carpeta_consultas, "Caracteristicas_de_los_nacimientos.csv"),
    index=False)


#%%--------------------------------------------------------------------------------
#CONSULTA 4

edad_fertil = ['15 a 19', '20 a 24', '25 a 29', '30 a 34', '35 a 39', '40 a 44', '45 a 49']

mujeres_2022_SQL = """
    SELECT id_provincia, grupo_etario, SUM(cantidad) AS cant_mujeres
    FROM habitante
    WHERE anio = 2022 AND grupo_etario IN ('15 a 19', '20 a 24', '25 a 29', '30 a 34', '35 a 39', '40 a 44', '45 a 49') AND sexo = 'mujer'
    GROUP BY id_provincia, grupo_etario
"""
mujeres_2022 = dd.sql(mujeres_2022_SQL).df()

nacidos_2022_SQL = """
    SELECT id_provincia, grupo_etario_madre AS grupo_etario, SUM(cantidad) AS cant_nacidos
    FROM nacimiento
    WHERE anio = 2022
    GROUP BY id_provincia, grupo_etario

"""
nacidos_2022 = dd.sql(nacidos_2022_SQL).df()

tasa_fecundidad_2022_SQL = """
    SELECT p.nombre AS provincia, m.grupo_etario, 
    ROUND(n.cant_nacidos/m.cant_mujeres*1000, 2) AS tasa_fecundidad
    FROM mujeres_2022 AS m
    JOIN nacidos_2022 AS n
    ON m.id_provincia = n.id_provincia AND m.grupo_etario = n.grupo_etario
    JOIN provincia AS p
    ON p.id = m.id_provincia 
    ORDER BY p.nombre, m.grupo_etario
"""
tasa_fecundidad_2022 = dd.sql(tasa_fecundidad_2022_SQL).df()

tasa_fecundidad_2022.to_csv(
    os.path.join(carpeta_consultas, "Tasa_fecundidad_2022.csv"),
    index=False)


#%%---------------------------------------------------------------------------------
#CONSULTA 5
porcentaje_madres_menores_2022_SQL = """
    WITH cantidades_22 AS (
        SELECT id_provincia, SUM(cantidad) AS total_nacidos, 
        SUM(CASE WHEN grupo_etario_madre IN ('Menor de 15','15 a 19') THEN cantidad ELSE 0 END) AS cant_madres_menores_20
        FROM nacimiento 
        WHERE anio = 2022
        GROUP BY id_provincia
    )
    SELECT id_provincia, (cant_madres_menores_20*100.0/total_nacidos) AS porcentaje_madres_menores_2022
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
    SELECT id_provincia, (cant_madres_menores_20*100.0/total_nacidos) AS porcentaje_madres_menores_2010
    FROM cantidades_10
    ORDER BY id_provincia
"""
porcentaje_madres_menores_2010 = dd.sql(porcentaje_madres_menores_2010_SQL).df()

cambios_edad_madresSQL = """
    SELECT p.nombre AS provincia, ROUND(p10.porcentaje_madres_menores_2010 - p22.porcentaje_madres_menores_2022, 2) AS diferencia_porcetaje
    FROM porcentaje_madres_menores_2022 AS p22
    JOIN porcentaje_madres_menores_2010 AS p10
    ON p22.id_provincia = p10.id_provincia
    JOIN provincia AS p
    ON p.id = p22.id_provincia
    ORDER BY diferencia_porcetaje DESC
"""
cambios_edad_madres = dd.sql(cambios_edad_madresSQL).df()

cambios_edad_madres.to_csv(
    os.path.join(carpeta_consultas, "Cambios_en_la_edad_de_las_madres.csv"), index=False)

#%%---------------------------------------------------------------------------------------

#PASAR LAS CONSULTAS A EXCEL

cant_habitantes_con_sin_cobertura.to_excel(
    os.path.join(carpeta_consultas, "Cobertura_de_salud.xlsx"),
    index=False)

establecimientos_con_terapia_intensiva.to_excel(
    os.path.join(carpeta_consultas, "Establecimientos_de_salud_con_terapia_intensiva.xlsx"),
    index=False)

caracteristicas_nacimientos.to_excel(
    os.path.join(carpeta_consultas, "Caracteristicas_de_los_nacimientos.xlsx"),
    index=False)

tasa_fecundidad_2022.to_excel(
    os.path.join(carpeta_consultas, "Tasa_fecundidad_2022.xlsx"),
    index=False)

cambios_edad_madres.to_excel(
    os.path.join(carpeta_consultas, "Cambios_en_la_edad_de_las_madres.xlsx"), index=False)

#%%---------------------------------------------------------------------------------------
# GRÁFICOS
#%%
print(censo_10.iloc[:,2])

posiciones_str2010=[]
lista_str2010 =[]
for i in range(len(censo_10)):
    v=censo_10.iloc[i,2]
    if (isinstance(v, str)& (v!=" Total")&(v!="Edad")):
        posiciones_str2010 = posiciones_str2010 + [i]
        lista_str2010 = lista_str2010 + [v]
    
#%%
#Busco posicion donde empieza el resumen
pos_resumen_10 = 0
for i in range(len(censo_10)):
    v=censo_10.iloc[i,1]
    if (isinstance(v, str)& (v=="RESUMEN")):
        pos_resumen_10 = i
        
#%%

cant_hab2010=[]
for i in range(1,len(lista_str2010)):
    a = censo_10.iloc[ posiciones_str2010[i]- 2 ,5]
    cant_hab2010=cant_hab2010 + [a] 

cant_hab2010 = cant_hab2010 +  [censo_10.iloc[pos_resumen_10-2,5]]


#%%
posiciones_str2022=[]
lista_str2022 =[]
for i in range(len(censo_22)):
    v=censo_22.iloc[i,2]
    if (isinstance(v, str)& (v!=" Total")&(v!="Edad")):
        posiciones_str2022 = posiciones_str2022 + [i]
        lista_str2022 = lista_str2022 + [v] 
#%%
#Busco posicion donde empieza el resumen
pos_resumen_22 = 0
for i in range(len(censo_22)):
    v=censo_22.iloc[i,1]
    if (isinstance(v, str)& (v=="RESUMEN")):
        pos_resumen_22 = i

#%%
cant_hab2022=[]
for i in range(1,len(lista_str2022)):
    a = censo_22.iloc[ posiciones_str2022[i]- 2 ,5]
    cant_hab2022=cant_hab2022 + [a]
    
cant_hab2022 = cant_hab2022 + [censo_22.iloc[pos_resumen_22-2,5]] 


#%%
#GRAFICO POBLACION POR PROVINCIA EN 2010VS2022

fig, ax = plt.subplots(figsize=(8, 10))
y = np.arange(len(lista_str2010))
ax.barh(y - 0.4/2, cant_hab2010, 0.4, label='2010', color="#4A4063")
ax.barh(y + 0.4/2, cant_hab2022, 0.4, label='2022', color='skyblue')
ax.set_yticks(y)
ax.set_yticklabels(lista_str2010)
ax.invert_yaxis()
ax.legend()
fig.tight_layout()

#%%
#Nacimientos prematuros según provincia
#Realizar un gráfico que muestre el porcentaje de nacimientos con menos de
#37 semanas de gestación por provincia, comparando los años 2010 y 2022.

nacimientos = pd.read_csv("nacimiento.csv")
provincia = pd.read_csv("provincia.csv")

#%%
nacimientos2010 = nacimientos.iloc[nacimientos["año"] == 2010, :].reset_index()
nacimientos2022 = nacimientos.iloc[nacimientos["año"] == 2022, :].reset_index()

len(nacimientos2010) + len(nacimientos2022) == len(nacimientos) #verificacion
#%%
np.unique(nacimientos2010["tipo_gestacion"])
prematuros2010Bool = (nacimientos2010["tipo_gestacion"]!= "37 a 41") & (nacimientos2010["tipo_gestacion"]!= "42 y más") 

prematuros2010 = nacimientos2010.iloc[prematuros2010Bool, :].reset_index()
np.unique(prematuros2010["tipo_gestacion"]) #verificacion
#%%
np.unique(nacimientos2022["tipo_gestacion"])
prematuros2022Bool = (nacimientos2022["tipo_gestacion"]!= "37 a 41") & (nacimientos2022["tipo_gestacion"]!= "42 y más") 

prematuros2022 = nacimientos2022.iloc[prematuros2022Bool, :].reset_index()
np.unique(prematuros2022["tipo_gestacion"]) #verificacion
#%%
#porcentaje de prematuros por provincia 2010

lista_prov2010 = []
vector_id_provincias2010 = np.unique(prematuros2010["id_provincia"])
for v in vector_id_provincias2010:
    contador_prem = 0
    contador_tot = 0
    for i in range(len(prematuros2010)):
        if prematuros2010['id_provincia'][i] == v:
            contador_prem += prematuros2010['cantidad'][i]      
    for j in range(len(nacimientos2010)):
        if nacimientos2010['id_provincia'][j] == v:
            contador_tot += nacimientos2010['cantidad'][j]
    porcentaje2010 = ((contador_prem)/(contador_tot))*100                  
    lista_prov2010.append(porcentaje2010) 
#%%
#porcentaje de prematuros por provincia 2022

lista_prov2022 = []
vector_id_provincias2022 = np.unique(prematuros2022["id_provincia"])
for v in vector_id_provincias2022:
    contador_prem = 0
    contador_tot = 0
    for i in range(len(prematuros2022)):
        if prematuros2022['id_provincia'][i] == v:
            contador_prem += prematuros2022['cantidad'][i]      
    for j in range(len(nacimientos2022)):
        if nacimientos2022['id_provincia'][j] == v:
            contador_tot += nacimientos2022['cantidad'][j]
    porcentaje2022 = ((contador_prem)/(contador_tot))*100                  
    lista_prov2022.append(porcentaje2022)     

#%%
#GRAFICO PORCENTAJE DE PREMATUROS 

prov = provincia['nombre']
x = np.arange(len(prov))

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(x - 0.3/2, lista_prov2010, 0.3,
       label='Porcentaje de prematuros en 2010', color='#4A4063')
ax.bar(x + 0.3/2, lista_prov2022, 0.3,
       label='Porcentaje de prematuros en 2022', color='skyblue')

ax.set_xticks(x)
ax.set_xticklabels(prov, rotation=45, ha='right')
ax.set_ylabel('Porcentaje de prematuros')
ax.legend()
fig.tight_layout()
plt.show()

#%%
habitantes = pd.read_csv('habitante.csv')
#%%
nacimientos2022 = nacimientos.iloc[nacimientos["año"] == 2022, :].reset_index()
#%%
#np.unique(nacimientos2022["rango_edad_madre"])
#total_madres2022 = np.sum(nacimientos2022["rango_edad_madre"]!= "Menor de 15")
#%%
habitantes2022 = habitantes.iloc[habitantes["año"] == 2022, :].reset_index()
mujeres2022 = habitantes2022.iloc[habitantes2022["sexo"] == 'mujer',:].reset_index()
#np.unique(mujeres2022["grupo_etario"])
#mujeres_fertiles2022Bool = (mujeres2022["grupo_etario"] != '0 a 4') & (mujeres2022["grupo_etario"]!= '5 a 9') & (mujeres2022["grupo_etario"]!= '10 a 14')
#total_mujeres2022 = np.sum(mujeres_fertiles2022Bool)
#%%
mujeres2022 = mujeres2022[(mujeres2022['id_provincia'] != 94) |
                          (mujeres2022['cantidad'] < 20000)].reset_index(drop=True)
#%%
#lista de mujeres en edad fertil por provincia 

lista_fertiles22 = []
for v in np.unique(mujeres2022["id_provincia"]):
    mujeres_fertiles_por_prov = 0
    for i in range(len(mujeres2022)):
        if ((mujeres2022['id_provincia'][i] == v) & 
            ((mujeres2022["grupo_etario"][i] == '15 a 19') | (mujeres2022["grupo_etario"][i]== '20 a 24') | (mujeres2022["grupo_etario"][i]== '25 a 29')
            & (mujeres2022["grupo_etario"][i]== '30 a 34') | (mujeres2022["grupo_etario"][i]== '35 a 39')| (mujeres2022["grupo_etario"][i]== '40 a 44')
            | (mujeres2022["grupo_etario"][i]== '45 a 49'))):
            mujeres_fertiles_por_prov += mujeres2022['cantidad'][i]
    
    lista_fertiles22.append(mujeres_fertiles_por_prov)
    
#%%
# lista de madres por provincia    
# total_madres2022 = np.sum(nacimientos2022["rango_edad_madre"]!= "Menor de 15")        
lista_madres22 = []   
for v in np.unique(nacimientos2022['id_provincia']):
    madres_por_provincia = 0 
    for i in range(len(nacimientos2022)):
        if ((nacimientos2022['id_provincia'][i] == v) & (nacimientos2022["rango_edad_madre"][i] != "Menor de 15")):
            madres_por_provincia += nacimientos['cantidad'][i]
    lista_madres22.append(madres_por_provincia)
    
#%%
# TASA DE FERTILIDAD CADA MIL 

tasa = ((np.array(lista_madres22))/(np.array(lista_fertiles22)))*1000    

#%%
#GRAFICO FERTILIDAD DE MENRO A MAYOR
df = pd.DataFrame({'provincia': provincia['nombre'], 'tasa': tasa}).sort_values('tasa')

x = np.arange(len(df))

fig, ax = plt.subplots(figsize=(16, 6))
ax.bar(x, df['tasa'], color='skyblue')

ax.set_xticks(x)
ax.set_xticklabels(df['provincia'], rotation=45, ha='right', fontsize=8)
ax.set_ylabel('Tasa')
ax.set_title('Tasa de fertilidad por provincia')

fig.tight_layout()
plt.show()
#%%
#GRAFICO TASA VS NIVEL DE INSTRUCCIÓN DE LA MADRE

niveles = ['Hasta Primaria/C.EGB Completa',
           'Secundaria/Polimodal Incompleta',
           'Secundario/Polimodal Completa y más']

df = nacimientos[(nacimientos['año'] == 2022) &
                 (nacimientos['nivel_instruccion_madre'].isin(niveles))]

tabla = df.pivot_table(index='id_provincia',
                       columns='nivel_instruccion_madre',
                       values='cantidad',
                       aggfunc='sum',
                       fill_value=0)[niveles]      # fija el orden de las 3 barras

# Reemplazar el código por el nombre de la provincia
nombres = provincia.set_index('id')['nombre']
tabla.index = tabla.index.map(nombres)

fig, ax = plt.subplots(figsize=(16, 6))
tabla.plot(kind='bar', ax=ax, color=['#4A4063', 'skyblue', '#8FBC8F'], width=0.8)

ax.set_xlabel('')
ax.set_ylabel('Cantidad de nacimientos')
ax.set_title('Nivel de instrucción de la madre por provincia (2022)')
ax.legend(title='Nivel de instrucción')
plt.xticks(rotation=45, ha='right')
fig.tight_layout()
plt.show()

#%%

muj = mujeres2022[(mujeres2022['sexo'] == 'mujer') &
                  (mujeres2022['año'] == 2022)]

m1 = muj[muj['grupo_etario'] == '15 a 19'].groupby('id_provincia')['cantidad'].sum()

m2 = muj[(muj['grupo_etario'] == '20 a 24') |
         (muj['grupo_etario'] == '25 a 29') |
         (muj['grupo_etario'] == '30 a 34')].groupby('id_provincia')['cantidad'].sum()

m3 = muj[(muj['grupo_etario'] == '35 a 39') |
         (muj['grupo_etario'] == '40 a 44') |
         (muj['grupo_etario'] == '45 a 49')].groupby('id_provincia')['cantidad'].sum()

#%%
nac = nacimientos[nacimientos['año'] == 2022]

# Nacimientos por provincia en cada grupo de edad de la madre
nac1 = nac[nac['rango_edad_madre'] == '15 a 19'].groupby('id_provincia')['cantidad'].sum()

nac2 = nac[(nac['rango_edad_madre'] == '20 a 24') |
           (nac['rango_edad_madre'] == '25 a 29') |
           (nac['rango_edad_madre'] == '30 a 34')].groupby('id_provincia')['cantidad'].sum()

nac3 = nac[(nac['rango_edad_madre'] == '35 a 39') |
           (nac['rango_edad_madre'] == '40 a 44') |
           (nac['rango_edad_madre'] == '45 a 49')].groupby('id_provincia')['cantidad'].sum()

# Mujeres por provincia en los mismos grupos de edad
m1 = mujeres2022[(mujeres2022['edad'] >= 15) & (mujeres2022['edad'] <= 19)].groupby('id_provincia')['cantidad'].sum()
m2 = mujeres2022[(mujeres2022['edad'] >= 20) & (mujeres2022['edad'] <= 34)].groupby('id_provincia')['cantidad'].sum()
m3 = mujeres2022[(mujeres2022['edad'] >= 35) & (mujeres2022['edad'] <= 49)].groupby('id_provincia')['cantidad'].sum()

# Tasas cada 1000 mujeres (se dividen alineadas por id_provincia)
tasas = pd.DataFrame({
    '15 a 19': nac1 / m1 * 1000,
    '20 a 34': nac2 / m2 * 1000,
    '35 a 49': nac3 / m3 * 1000,
})
tasas['total'] = (nac1 + nac2 + nac3) / (m1 + m2 + m3) * 1000

# Traer el nombre de la provincia y ordenar de menor a mayor
tasas = tasas.reset_index()
tasas = tasas.merge(provincia, left_on='id_provincia', right_on='id')
tasas = tasas.sort_values('total')

#%%
x = np.arange(len(tasas))
ancho = 0.27

fig, ax = plt.subplots(figsize=(16, 6))
ax.bar(x - ancho, tasas['15 a 19'], ancho, label='15 a 19', color='#4A4063')
ax.bar(x,         tasas['20 a 34'], ancho, label='20 a 34', color='skyblue')
ax.bar(x + ancho, tasas['35 a 49'], ancho, label='35 a 49', color='#8FBC8F')

ax.set_xticks(x)
ax.set_xticklabels(tasas['nombre'], rotation=45, ha='right', fontsize=8)
ax.set_ylabel('Nacimientos cada 1000 mujeres del grupo')
ax.set_title('Tasa de fecundidad por provincia y grupo de edad, 2022')
ax.legend(title='Edad de la madre')
fig.tight_layout()
plt.show()

#%%

nac = nacimientos[nacimientos['año'] == 2022]

# Nacimientos por provincia y grupo de edad de la madre
nac1 = nac[nac['rango_edad_madre'] == '15 a 19'].groupby('id_provincia')['cantidad'].sum()

nac2 = nac[(nac['rango_edad_madre'] == '20 a 24') |
           (nac['rango_edad_madre'] == '25 a 29') |
           (nac['rango_edad_madre'] == '30 a 34')].groupby('id_provincia')['cantidad'].sum()

nac3 = nac[(nac['rango_edad_madre'] == '35 a 39') |
           (nac['rango_edad_madre'] == '40 a 44') |
           (nac['rango_edad_madre'] == '45 a 49')].groupby('id_provincia')['cantidad'].sum()

# Mujeres por provincia y grupo de edad (usa grupo_etario, no edad)
muj = mujeres2022[(mujeres2022['sexo'] == 'mujer') &
                  (mujeres2022['año'] == 2022)]

m1 = muj[muj['grupo_etario'] == '15 a 19'].groupby('id_provincia')['cantidad'].sum()

m2 = muj[(muj['grupo_etario'] == '20 a 24') |
         (muj['grupo_etario'] == '25 a 29') |
         (muj['grupo_etario'] == '30 a 34')].groupby('id_provincia')['cantidad'].sum()

m3 = muj[(muj['grupo_etario'] == '35 a 39') |
         (muj['grupo_etario'] == '40 a 44') |
         (muj['grupo_etario'] == '45 a 49')].groupby('id_provincia')['cantidad'].sum()

# Tasas cada 1000 mujeres
tasas = pd.DataFrame({
    '15 a 19': nac1 / m1 * 1000,
    '20 a 34': nac2 / m2 * 1000,
    '35 a 49': nac3 / m3 * 1000,
})
tasas['total'] = (nac1 + nac2 + nac3) / (m1 + m2 + m3) * 1000

tasas = tasas.reset_index()
tasas = tasas.merge(provincia, left_on='id_provincia', right_on='id')
tasas = tasas.sort_values('total')

print(tasas.head())

#%%
nac = nacimientos[nacimientos['año'] == 2022]
nivel = nac['nivel_instruccion_madre']

total = nac.groupby('id_provincia')['cantidad'].sum()

p1 = nac[nivel == 'Hasta Primaria/C.EGB Completa'].groupby('id_provincia')['cantidad'].sum() / total * 100
p2 = nac[nivel == 'Secundaria/Polimodal Incompleta'].groupby('id_provincia')['cantidad'].sum() / total * 100
p3 = nac[nivel.str.startswith('Secundario/Polimodal Completa')].groupby('id_provincia')['cantidad'].sum() / total * 100

instr = pd.DataFrame({
    'Hasta primaria completa': p1,
    'Secundaria incompleta': p2,
    'Secundario completa y más': p3,
}).reset_index()

instr = instr.merge(provincia, left_on='id_provincia', right_on='id')
instr = instr.sort_values('Hasta primaria completa')

print(instr.head())

#%%
x = np.arange(len(instr))
ancho = 0.27

fig, ax = plt.subplots(figsize=(16, 6))
ax.bar(x - ancho, instr['Hasta primaria completa'], ancho, label='Hasta primaria completa', color='#4A4063')
ax.bar(x,         instr['Secundaria incompleta'], ancho, label='Secundaria incompleta', color='skyblue')
ax.bar(x + ancho, instr['Secundario completa y más'], ancho, label='Secundaria completa y más', color='#8FBC8F')

ax.set_xticks(x)
ax.set_xticklabels(instr['nombre'], rotation=45, ha='right', fontsize=8)
ax.set_ylabel('% de nacimientos')
ax.set_title('Nivel de instrucción de la madre por provincia, 2022')
ax.legend()
fig.tight_layout()
plt.show()

#%%
lista_fertiles22 = []
for v in np.unique(mujeres2022["id_provincia"]):
    mujeres_fertiles_por_prov = 0
    for i in range(len(mujeres2022)):
        g = mujeres2022["grupo_etario"][i]
        if (mujeres2022['id_provincia'][i] == v) & \
           ((g == '15 a 19') | (g == '20 a 24') | (g == '25 a 29') |
            (g == '30 a 34') | (g == '35 a 39') | (g == '40 a 44') |
            (g == '45 a 49')):
            mujeres_fertiles_por_prov += mujeres2022['cantidad'][i]
    lista_fertiles22.append(mujeres_fertiles_por_prov)

#%%
lista_madres22 = []
for v in np.unique(nacimientos2022['id_provincia']):
    madres_por_provincia = 0
    for i in range(len(nacimientos2022)):
        if ((nacimientos2022['id_provincia'][i] == v) &
            (nacimientos2022["rango_edad_madre"][i] != "Menor de 15")):
            madres_por_provincia += nacimientos2022['cantidad'][i]   # <- nacimientos2022
    lista_madres22.append(madres_por_provincia)

#%%
tasa = (np.array(lista_madres22) / np.array(lista_fertiles22)) * 1000

#%%
# Se pega por id, no por posición
ids = np.unique(mujeres2022["id_provincia"])
df = pd.DataFrame({'id_provincia': ids, 'tasa': tasa})
df = df.merge(provincia, left_on='id_provincia', right_on='id')
df = df.sort_values('tasa')
print(df)


#%%
# GRAFICO 1: tasa de fecundidad por provincia, 2022
x = np.arange(len(df))

fig, ax = plt.subplots(figsize=(16, 6))
ax.bar(x, df['tasa'], color='skyblue')

ax.set_xticks(x)
ax.set_xticklabels(df['nombre'], rotation=45, ha='right', fontsize=8)
ax.set_ylabel('Nacimientos cada 1000 mujeres de 15 a 49 años')
ax.set_title('Tasa de fecundidad por provincia, 2022')

fig.tight_layout()
plt.show()


#%%
nac = nacimientos[nacimientos['año'] == 2022]
nivel = nac['nivel_instruccion_madre']
bajo = nac['peso_hijo'] == 'Menos de 2500 gramos'

n1 = nivel == 'Hasta Primaria/C.EGB Completa'
n2 = nivel == 'Secundaria/Polimodal Incompleta'
n3 = nivel.str.startswith('Secundario/Polimodal Completa')


tot1 = nac[n1].groupby('id_provincia')['cantidad'].sum()
tot2 = nac[n2].groupby('id_provincia')['cantidad'].sum()
tot3 = nac[n3].groupby('id_provincia')['cantidad'].sum()


bajo1 = nac[n1 & bajo].groupby('id_provincia')['cantidad'].sum()
bajo2 = nac[n2 & bajo].groupby('id_provincia')['cantidad'].sum()
bajo3 = nac[n3 & bajo].groupby('id_provincia')['cantidad'].sum()

bp = pd.DataFrame({
    'Hasta primaria completa': (bajo1 / tot1 * 100).fillna(0),
    'Secundaria incompleta': (bajo2 / tot2 * 100).fillna(0),
    'Secundaria completa y más': (bajo3 / tot3 * 100).fillna(0),
}).reset_index()

bp = bp.merge(provincia, left_on='id_provincia', right_on='id')
bp = bp.sort_values('Hasta primaria completa')
print(bp.head())

#%%
x = np.arange(len(bp))
ancho = 0.27

fig, ax = plt.subplots(figsize=(16, 6))
ax.bar(x - ancho, bp['Hasta primaria completa'], ancho,
       label='Hasta primaria completa', color='#4A4063')
ax.bar(x, bp['Secundaria incompleta'], ancho,
       label='Secundaria incompleta', color='skyblue')
ax.bar(x + ancho, bp['Secundaria completa y más'], ancho,
       label='Secundaria completa y más', color='#8FBC8F')

ax.set_xticks(x)
ax.set_xticklabels(bp['nombre'], rotation=45, ha='right', fontsize=8)
ax.set_ylabel('% de nacimientos con bajo peso (< 2500 g)')
ax.set_title('Bajo peso al nacer según nivel de instrucción de la madre por provincia 2022')
ax.legend(title='Nivel de instrucción')

fig.tight_layout()
plt.show()



#%%
centros_salud = pd.read_csv('centro_de_salud.csv')


#%%
por_depto = centros_salud.groupby(['provincia_id', 'departamento_id']).size().reset_index(name='cantidad')

#%%
datos = []
nombres = []
for v in np.unique(por_depto['provincia_id']):
    datos.append(por_depto[por_depto['provincia_id'] == v]['cantidad'].values)
    nombres.append(provincia[provincia['id'] == v]['nombre'].values[0])

# Ordenar por la mediana (opcional)
orden = np.argsort([np.median(d) for d in datos])
datos = [datos[i] for i in orden]
nombres = [nombres[i] for i in orden]
#%%
fig, ax = plt.subplots(figsize=(16, 6))
ax.boxplot(datos)

ax.set_xticks(np.arange(1, len(nombres) + 1))
ax.set_xticklabels(nombres, rotation=45, ha='right', fontsize=8)
ax.set_ylabel('Establecimientos de salud por departamento')
ax.set_title('Distribución de establecimientos de salud por departamento, según provincia')

fig.tight_layout()
plt.show()

#no se ve casi nada aca, paso a probar en  otra escala
#%%
#escala logaritmica para que se vea mejorr
fig, ax = plt.subplots(figsize=(16, 7))
ax.boxplot(datos)

ax.set_yscale('log')

ax.set_xticks(np.arange(1, len(nombres) + 1))
ax.set_xticklabels(nombres, rotation=45, ha='right', fontsize=8)
ax.set_ylabel('Establecimientos de salud por departamento (escala log)')
ax.set_title('Distribución de establecimientos de salud por departamento, según provincia')
ax.grid(axis='y', alpha=0.3)

fig.tight_layout()
plt.show()



#%%

#Instrucción de la madre vs. bajo peso por provincia

nac = nacimientos[nacimientos['año'] == 2022]

total = nac.groupby('id_provincia')['cantidad'].sum()
bajo = nac[nac['peso_hijo'] == 'Menos de 2500 gramos'].groupby('id_provincia')['cantidad'].sum()
prim = nac[nac['nivel_instruccion_madre'] == 'Hasta Primaria/C.EGB Completa'].groupby('id_provincia')['cantidad'].sum()

sc = pd.DataFrame({
    'pct_primaria': prim / total * 100,
    'pct_bajo': bajo / total * 100,
}).reset_index()
sc = sc.merge(provincia, left_on='id_provincia', right_on='id')
print(sc.head())

#%%
d = bp.copy()
d['brecha'] = d['Hasta primaria completa'] - d['Secundaria completa y más']
d = d.sort_values('brecha')

prim = d['Hasta primaria completa'].values
sec = d['Secundaria completa y más'].values
y = np.arange(len(d))

fig, ax = plt.subplots(figsize=(10, 9))
ax.hlines(y, sec, prim, color='lightgray', linewidth=2, zorder=1)
ax.scatter(prim, y, color='#4A4063', s=50, label='Hasta primaria completa', zorder=2)
ax.scatter(sec, y, color='skyblue', s=50, label='Secundaria completa y más', zorder=2)

ax.set_yticks(y)
ax.set_yticklabels(d['nombre'].values, fontsize=8)
ax.set_xlabel('% de nacimientos con bajo peso (< 2500 g)')
ax.set_title('Bajo peso al nacer según instrucción de la madre por provincia (2022)')
ax.legend()
ax.grid(axis='x', alpha=0.3)

fig.tight_layout()
plt.show()

