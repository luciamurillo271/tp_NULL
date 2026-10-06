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
# Joineamos censos 10 y censos 22

total_habitantesSQL = """
    SELECT * 
    FROM censo_10, 
    UNION 
    SELECT * 
    FROM censo_22
"""

total_habitantes = dd.sql(total_habitantesSQL).df()
total_habitantes["cantidad"] = pd.to_numeric(total_habitantes["cantidad"], errors="coerce")

#agrupamos cantidades de misma provincia, sexo, cobertura, grupo etario y año
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
    
#ARMAMOS CSV DE PROVINCIA
provincia.to_csv(
    os.path.join(carpeta_modelo, "provincia.csv"),
    index=False
)

#%%-----------------------------------------------------------------------------------------------
#creamos tabla DEPARTAMENTO a partir de datos de establecimientos de salud
departamentoSQL = """
                SELECT DISTINCT "departamento_id" AS id, "departamento_nombre" AS nombre, "provincia_id" AS provincia_id
                FROM establecimientos_de_salud
                ORDER BY id
                
            """
departamento = dd.sql(departamentoSQL).df()

#ARMAMOS CSV DE DEPARTAMENTO
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


#CONSULTAS
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
    ORDER BY p.nombre, h10.grupo_etario
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
nacidos_por_provincia_y_edad_madre_SQL = """
    SELECT id_provincia, grupo_etario_madre, anio, SUM(cantidad) AS cantidad_total
    FROM nacimiento
    GROUP BY id_provincia, grupo_etario_madre, anio
    ORDER BY id_provincia, grupo_etario_madre
"""
nacidos_total = dd.sql(nacidos_por_provincia_y_edad_madre_SQL).df()

cant_bajo_peso_por_prov_y_edad_madre_SQL = """
    SELECT id_provincia, grupo_etario_madre, anio, SUM(cantidad) AS cantidad
    FROM nacimiento
    WHERE peso_bebe = 'Menos de 2500 gramos'
    GROUP BY id_provincia, grupo_etario_madre, anio
    ORDER BY id_provincia, grupo_etario_madre
"""
bajo_peso = dd.sql(cant_bajo_peso_por_prov_y_edad_madre_SQL).df()

consulta3 = """
    SELECT t.anio, t.id_provincia, t.grupo_etario_madre, t.cantidad_total AS cantidad_nacimientos, ROUND(bp.cantidad*100.0/t.cantidad_total, 2) AS porcentaje_bajo_peso
    FROM nacidos_total AS t
    JOIN bajo_peso AS bp
    ON t.id_provincia = bp.id_provincia AND t.anio = bp.anio AND t.grupo_etario_madre = bp.grupo_etario_madre
    ORDER BY t.id_provincia, t.grupo_etario_madre, t.anio
"""
consulta_df = dd.sql(consulta3).df()

consulta_df.to_csv(
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