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