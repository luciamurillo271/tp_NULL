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
#LIMPIEZA DE DATOS NACIDOS VIVOS 10

#columnas que queremos con los nombres que queremos
nacidos_10 = nacidos_10[["IMEDAD", "PROVRES", "IMINSTRUC", "ITIEMGEST", "IPESONAC", "CUENTA"]].copy()
nacidos_10["año"] = 2010
nacidos_10 = nacidos_10.rename(columns={
    "IMEDAD" : "rango_edad_madre",
    "PROVRES" : "id_provincia",
    "IMINSTRUC": "nivel_instruccion_madre",
    "ITIEMGEST": "tipo_gestacion",
    "IPESONAC": "peso_hijo",
    "CUENTA": "cantidad"
    })
#queremos sacar el numero antes del rango etario, str split parte el texto en el punto, tomamos la segunda parte
nacidos_10["rango_edad_madre"] = nacidos_10["rango_edad_madre"].str.split(".", n=1).str[1]
nacidos_10["nivel_instruccion_madre"] = nacidos_10["nivel_instruccion_madre"].str.split(".", n=1).str[1]
nacidos_10["tipo_gestacion"] = nacidos_10["tipo_gestacion"].str.split(".", n=1).str[1]
nacidos_10["peso_hijo"] = nacidos_10["peso_hijo"].str.split(".", n=1).str[1]
#print(nacidos_10)

#algunas preguntas
print(nacidos_10.shape)
print(nacidos_10.dtypes)
print(nacidos_10.isna().sum()) # no hay nulls explicitos
print(nacidos_10["rango_edad_madre"].value_counts(dropna=False).sort_index())

#borramos filas con "sin especificar"
columnas = nacidos_10.columns.tolist()
for col in columnas:
    nacidos_10[col] = nacidos_10[col].replace('Sin especificar', None)
nacidos_10["id_provincia"] = nacidos_10["id_provincia"].replace('98', None)
nacidos_10["id_provincia"] = nacidos_10["id_provincia"].replace('99', None)
nacidos_10 = nacidos_10.dropna()

print(nacidos_10)

print(nacidos_10.shape)
print(nacidos_10.dtypes)
print(nacidos_10.isna().sum()) # no hay nulls explicitos
print(nacidos_10["rango_edad_madre"].value_counts(dropna=False).sort_index())
#print(nacidos_22.shape())

#%%--------------
#LIMPIEZA NACIDOS VIVOS 22
#columnas que queremos con los nombres que queremos
print(nacidos_22.shape)
nacidos_22 = nacidos_22[["IMEDAD", "PROVRES", "IMINSTRUC", "ITIEMGEST", "IPESONAC", "CUENTA"]].copy()
nacidos_22["año"] = 2022
nacidos_22 = nacidos_22.rename(columns={
    "IMEDAD" : "rango_edad_madre",
    "PROVRES" : "id_provincia",
    "IMINSTRUC": "nivel_instruccion_madre",
    "ITIEMGEST": "tipo_gestacion",
    "IPESONAC": "peso_hijo",
    "CUENTA": "cantidad"
    })
#queremos sacar el numero antes del rango etario, str split parte el texto en el punto, tomamos la segunda parte
nacidos_22["rango_edad_madre"] = nacidos_22["rango_edad_madre"].str.split(".", n=1).str[1]
nacidos_22["nivel_instruccion_madre"] = nacidos_22["nivel_instruccion_madre"].str.split(".", n=1).str[1]
nacidos_22["tipo_gestacion"] = nacidos_22["tipo_gestacion"].str.split(".", n=1).str[1]
nacidos_22["peso_hijo"] = nacidos_22["peso_hijo"].str.split(".", n=1).str[1]
#print(nacidos_22)

#algunas preguntas
print(nacidos_22.shape)
print(nacidos_22.dtypes)
print(nacidos_22.isna().sum()) # no hay nulls explicitos
print(nacidos_22["rango_edad_madre"].value_counts(dropna=False).sort_index())

#borramos filas con "sin especificar"
columnas = nacidos_22.columns.tolist()
for col in columnas:
    nacidos_22[col] = nacidos_22[col].replace('Sin especificar', None)
#nacidos_22["id_provincia"] = nacidos_22["id_provincia"].replace('98', None)
#nacidos_22["id_provincia"] = nacidos_22["id_provincia"].replace('99', None)
nacidos_22 = nacidos_22.dropna()

print(nacidos_22)

print(nacidos_22.shape)
print(nacidos_22.dtypes)
print(nacidos_22.isna().sum()) # no hay nulls explicitos
print(nacidos_22["rango_edad_madre"].value_counts(dropna=False).sort_index())

#%%
#JOIN TABLAS NACIDOS VIVOS
nacimiento = """
    SELECT * 
    FROM nacidos_10, 
    UNION 
    SELECT * 
    FROM nacidos_22
    ORDER BY id_provincia, rango_edad_madre, año
"""
nacimientos_df = dd.sql(nacimiento).df()
nacimientos_df = nacimientos_df[~nacimientos_df["id_provincia"].astype(str).isin(['98', '99'])]
print(nacimientos_df)
nacimientos_df.to_csv(carpeta_modelo + "nacimiento.csv", index=False)
#%%---------------------------------------------------------------------------------------------
#LIMPIEZA DE DATOS CENSOS
print(censo_10.shape)
#print(censo_10.head(40))
#columnas = censo_10.columns.tolist()
#print(columnas)
censo_10 = censo_10.iloc[:,1:6]
censo_10.columns = ["bloque", "edad","varon","mujer","total"]
#print(censo_10.head(120))

textos = censo_10["bloque"].fillna("").astype(str).str.strip().tolist()   # la columna de títulos, como lista de textos
print(textos[:100])
area_actual = None           # el área que estamos recorriendo
cobertura_actual = None      # la cobertura que estamos recorriendo
texto_anterior = ""          # lo que decía la fila de arriba

lista_area = []
lista_cobertura = []
coberturas = ["Obra social (incluye PAMI)", "Prepaga a través de obra social", "Prepaga sólo por contratación voluntaria", "Programas o planes estatales de salud", "No tiene obra social, prepaga o plan estatal", "Total"]

for texto in textos:
    # Si la fila es un título de área, nos acordamos del código (sin "AREA # ")
    if texto.startswith("AREA #"):
        area_actual = texto.replace("AREA # ", "")
    elif texto in coberturas:
        cobertura_actual = texto

    # En cada fila anotamos lo que "recordamos" hasta ahora
    lista_area.append(area_actual)
    lista_cobertura.append(cobertura_actual)

    texto_anterior = texto

print(lista_cobertura[:100])
print(lista_cobertura[15600:])

censo_10["id_provincia"] = lista_area
censo_10["cobertura"] = lista_cobertura
print(censo_10["cobertura"].value_counts())

sin_cobertura = ["No tiene obra social, prepaga o plan estatal"]
totales = ["Total"]
censo_10["tiene_cobertura"] = "Tiene"
censo_10.loc[censo_10["cobertura"].isin(sin_cobertura), "tiene_cobertura"] = "No tiene"
censo_10.loc[censo_10["cobertura"].isin(totales), "tiene_cobertura"] = None
print(censo_10.shape)
print(censo_10.tail(20))
censo_10 = censo_10.drop(columns=["bloque", "cobertura","total"])
censo_10 = censo_10.dropna()


varones = censo_10[["id_provincia", "edad", "varon","tiene_cobertura"]].rename(columns={"varon":"cantidad"})
varones["sexo"] = "varon"

mujeres = censo_10[["id_provincia", "edad", "mujer","tiene_cobertura"]].rename(columns={"mujer":"cantidad"})
mujeres["sexo"] = "mujer"

censo_10 = pd.concat([varones, mujeres], ignore_index=True)

censo_10["edad"] = pd.to_numeric(censo_10["edad"], errors="coerce")
censo_10 = censo_10.dropna(subset=["edad"])
censo_10["edad"] = censo_10["edad"].astype(int)

censo_10["edad_inicio"] = (censo_10["edad"] // 5) * 5
censo_10["edad_fin"] = censo_10["edad_inicio"] + 4

censo_10["grupo_etario"] = (censo_10["edad_inicio"].astype(str) + " a " + censo_10["edad_fin"].astype(str))
censo_10.loc[censo_10["edad"] >= 100, "grupo_etario"] = "100 y más"

censo_10 = censo_10.drop(columns=["edad", "edad_inicio","edad_fin"])
censo_10["año"] = 2010
print(censo_10.tail(20))

#%%
print(censo_22.shape)
censo_22 = censo_22.iloc[:,1:6]
censo_22.columns = ["bloque", "edad","varon","mujer","total"]

textos = censo_22["bloque"].fillna("").astype(str).str.strip().tolist()   # la columna de títulos, como lista de textos
print(textos[:100])
area_actual = None           # el área que estamos recorriendo
cobertura_actual = None      # la cobertura que estamos recorriendo
texto_anterior = ""          # lo que decía la fila de arriba

lista_area = []
lista_cobertura = []
coberturas = ["Obra social o prepaga (incluye PAMI)", "Programas o planes estatales de salud", "No tiene obra social, prepaga ni plan estatal", "Total"]

for texto in textos:
    # Si la fila es un título de área, nos acordamos del código (sin "AREA # ")
    if texto.startswith("AREA #"):
        area_actual = texto.replace("AREA # ", "")
    elif texto in coberturas:
        cobertura_actual = texto

    # En cada fila anotamos lo que "recordamos" hasta ahora
    lista_area.append(area_actual)
    lista_cobertura.append(cobertura_actual)

    texto_anterior = texto

censo_22["id_provincia"] = lista_area
censo_22["cobertura"] = lista_cobertura
print(censo_22["cobertura"].value_counts())

sin_cobertura = ["No tiene obra social, prepaga ni plan estatal"]
totales = ["Total"]
censo_22["tiene_cobertura"] = "Tiene"
censo_22.loc[censo_22["cobertura"].isin(sin_cobertura), "tiene_cobertura"] = "No tiene"
censo_22.loc[censo_22["cobertura"].isin(totales), "tiene_cobertura"] = None
#print(censo_22.shape)
#print(censo_22.tail(20))
censo_22 = censo_22.drop(columns=["bloque", "cobertura","total"])
censo_22 = censo_22.dropna()


varones = censo_22[["id_provincia", "edad", "varon","tiene_cobertura"]].rename(columns={"varon":"cantidad"})
varones["sexo"] = "varon"

mujeres = censo_22[["id_provincia", "edad", "mujer","tiene_cobertura"]].rename(columns={"mujer":"cantidad"})
mujeres["sexo"] = "mujer"

censo_22 = pd.concat([varones, mujeres], ignore_index=True)

censo_22["edad"] = pd.to_numeric(censo_22["edad"], errors="coerce")
censo_22 = censo_22.dropna(subset=["edad"])
censo_22["edad"] = censo_22["edad"].astype(int)

censo_22["edad_inicio"] = (censo_22["edad"] // 5) * 5
censo_22["edad_fin"] = censo_22["edad_inicio"] + 4

censo_22["grupo_etario"] = (censo_22["edad_inicio"].astype(str) + " a " + censo_22["edad_fin"].astype(str))
censo_22.loc[censo_22["edad"] >= 100, "grupo_etario"] = "100 y más"

censo_22 = censo_22.drop(columns=["edad", "edad_inicio","edad_fin"])
censo_22["año"] = 2022
#print(censo_22.tail(20))

#%%------------------------------------------------------------------------------
# Joineamos censos 10 y censos 22

habitanteSQL = """
    SELECT * 
    FROM censo_10, 
    UNION 
    SELECT * 
    FROM censo_22
    ORDER BY id_provincia, grupo_etario, año
"""

habitante = dd.sql(habitanteSQL).df()
habitante["cantidad"] = pd.to_numeric(habitante["cantidad"], errors="coerce")
#print(habitante)
habitante.to_csv(carpeta_modelo + "habitante.csv", index=False)
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

#%%-----------------------------------------------------------------------------------------------
#creamos tabla departamento a partir de datos de establecimientos de salud
departamentoSQL = """
                SELECT DISTINCT "departamento_id" AS id, "departamento_nombre" AS nombre, "provincia_id" AS provincia_id
                FROM establecimientos_de_salud
                ORDER BY id
                
            """
departamento = dd.sql(departamentoSQL).df()



departamento.to_csv(carpeta_modelo + "departamento.csv", index=False)

#%%
#LEEMOS NUESTRAS TABLAS
nacimiento = pd.read_csv(carpeta_modelo+"nacimiento.csv")
provincia = pd.read_csv(carpeta_modelo+"provincia.csv")
centro_de_salud = pd.read_csv(carpeta_modelo+"centro_de_salud.csv")

#%%----------------------------------------------------------------------------------
#CONSULTA 1
cant_habitantes_con_sin_cober_2010_SQL = """
    SELECT id_provincia, grupo_etario, 
    SUM(CASE WHEN año = 2010 AND tiene_cobertura = 'Tiene' THEN cantidad ELSE 0 END) AS con_cobertura,
    SUM(CASE WHEN año = 2010 AND tiene_cobertura = 'No tiene' THEN cantidad ELSE 0 END) AS sin_cobertura
    FROM habitante
    GROUP BY id_provincia, grupo_etario
"""
cant_habitantes_con_sin_cober_2010 = dd.sql(cant_habitantes_con_sin_cober_2010_SQL).df()

cant_habitantes_con_sin_cober_2022_SQL = """
    SELECT id_provincia, grupo_etario, 
    SUM(CASE WHEN año = 2022 AND tiene_cobertura = 'Tiene' THEN cantidad ELSE 0 END) AS con_cobertura,
    SUM(CASE WHEN año = 2022 AND tiene_cobertura = 'No tiene' THEN cantidad ELSE 0 END) AS sin_cobertura
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
print("HABITANTE")
print(cant_habitantes_con_sin_cobertura)

#%%---------------------------------------------------------------------------------------------
# BOCETO CONSULTA 2)
consulta = """
                SELECT p.nombre AS provincia, cs.origen_financiamiento, COUNT(*) AS cant_con_terapia_intensiva, 
                FROM centro_de_salud AS cs
                JOIN provincia AS p
                ON cs.provincia_id = p.id
                WHERE tipologia_nombre LIKE '%terapia intensiva%' AND cs.origen_financiamiento IN ('Estatal', 'Privado')
                GROUP BY p.nombre, cs.origen_financiamiento
                ORDER BY p.nombre, cs.origen_financiamiento
            """
consulta_df = dd.sql(consulta).df()
print(consulta_df)


'''
print(dd.sql("""
    SELECT COUNT(*) FROM centro_de_salud
    WHERE tipologia_nombre LIKE '%terapia intensiva%' AND origen_financiamiento IN ('Estatal', 'Privado')
""").df())
'''
#print(centro_de_salud.loc[centro_de_salud["tipologia_nombre"].str.contains("terapia intensiva"),"tipologia_nombre"].value_counts())

#%%--------------------------------------------------------------------------------
#CONSULTA 3
nacidos_por_provincia_y_edad_madre_SQL = """
    SELECT id_provincia, rango_edad_madre, año, SUM(cantidad) AS cantidad_total
    FROM nacimiento
    GROUP BY id_provincia, rango_edad_madre, año
    ORDER BY id_provincia, rango_edad_madre
"""
nacidos_total = dd.sql(nacidos_por_provincia_y_edad_madre_SQL).df()
print(nacidos_total)

cant_bajo_peso_por_prov_y_edad_madre_SQL = """
    SELECT id_provincia, rango_edad_madre, año, SUM(cantidad) AS cantidad
    FROM nacimiento
    WHERE peso_hijo = 'Menos de 2500 gramos'
    GROUP BY id_provincia, rango_edad_madre, año
    ORDER BY id_provincia, rango_edad_madre
"""
bajo_peso = dd.sql(cant_bajo_peso_por_prov_y_edad_madre_SQL).df()
print(bajo_peso)

consulta3 = """
    SELECT t.año, t.id_provincia, t.rango_edad_madre, t.cantidad_total, ROUND(bp.cantidad*100.0/t.cantidad_total, 2) AS porcentaje_bajo_peso
    FROM nacidos_total AS t
    JOIN bajo_peso AS bp
    ON t.id_provincia = bp.id_provincia AND t.año = bp.año AND t.rango_edad_madre = bp.rango_edad_madre
    ORDER BY t.id_provincia, t.rango_edad_madre, t.año
"""
consulta_df = dd.sql(consulta3).df()
print(consulta_df)

#%%--------------------------------------------------------------------------------
#CONSULTA 4

edad_fertil = ['15 a 19', '20 a 24', '25 a 29', '30 a 34', '35 a 39', '40 a 44', '45 a 49']

mujeres_2022_SQL = """
    SELECT id_provincia, grupo_etario, SUM(cantidad) AS cant_mujeres
    FROM habitante
    WHERE año = 2022 AND grupo_etario IN ('15 a 19', '20 a 24', '25 a 29', '30 a 34', '35 a 39', '40 a 44', '45 a 49') AND sexo = 'mujer'
    GROUP BY id_provincia, grupo_etario
"""
mujeres_2022 = dd.sql(mujeres_2022_SQL).df()

nacidos_2022_SQL = """
    SELECT id_provincia, rango_edad_madre AS grupo_etario, SUM(cantidad) AS cant_nacidos
    FROM nacimiento
    WHERE año = 2022
    GROUP BY id_provincia, grupo_etario

"""
nacidos_2022 = dd.sql(nacidos_2022_SQL).df()

tasa_fecundidad_2022_SQL = """
    SELECT p.nombre AS provincia, m.grupo_etario AS grupo_etario, 
    ROUND(n.cant_nacidos/m.cant_mujeres*1000, 2) AS tasa_fecundidad
    FROM mujeres_2022 AS m
    JOIN nacidos_2022 AS n
    ON m.id_provincia = n.id_provincia AND m.grupo_etario = n.grupo_etario
    JOIN provincia AS p
    ON p.id = m.id_provincia 
    ORDER BY p.nombre, m.grupo_etario
"""
tasa_fecundidad_2022 = dd.sql(tasa_fecundidad_2022_SQL).df()
print(tasa_fecundidad_2022)

#%%---------------------------------------------------------------------------------
#CONSULTA 5
porcentaje_madres_menores_2022 = """
    WITH cantidades_22 AS (
        SELECT id_provincia, SUM(cantidad) AS total_nacidos, 
        SUM(CASE WHEN rango_edad_madre IN ('Menor de 15','15 a 19') THEN cantidad ELSE 0 END) AS cant_madres_menores_20
        FROM nacimiento 
        WHERE año = 2022
        GROUP BY id_provincia
    )
    SELECT id_provincia, (cant_madres_menores_20*100.0/total_nacidos) AS porcentaje_madres_menores_2022
    FROM cantidades_22
    ORDER BY id_provincia
"""
porcentaje_madres_menores_2022_df = dd.sql(porcentaje_madres_menores_2022).df()
print(porcentaje_madres_menores_2022_df)

porcentaje_madres_menores_2010 = """
    WITH cantidades_10 AS (
        SELECT id_provincia, SUM(cantidad) AS total_nacidos, 
        SUM(CASE WHEN rango_edad_madre IN ('Menor de 15','15 a 19') THEN cantidad ELSE 0 END) AS cant_madres_menores_20
        FROM nacimiento 
        WHERE año = 2010
        GROUP BY id_provincia
    )
    SELECT id_provincia, (cant_madres_menores_20*100.0/total_nacidos) AS porcentaje_madres_menores_2010
    FROM cantidades_10
    ORDER BY id_provincia
"""
porcentaje_madres_menores_2010_df = dd.sql(porcentaje_madres_menores_2010).df()
print(porcentaje_madres_menores_2010_df)

cambios_edad_madres = """
    SELECT p.nombre AS provincia, ROUND(p10.porcentaje_madres_menores_2010 - p22.porcentaje_madres_menores_2022, 2) AS diferencia_porcetaje
    FROM porcentaje_madres_menores_2022_df AS p22
    JOIN porcentaje_madres_menores_2010_df AS p10
    ON p22.id_provincia = p10.id_provincia
    JOIN provincia AS p
    ON p.id = p22.id_provincia
    ORDER BY diferencia_porcetaje DESC
"""
cambios_edad_madres_df = dd.sql(cambios_edad_madres).df()
print(cambios_edad_madres_df)
# %%
