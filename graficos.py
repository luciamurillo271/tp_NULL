# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd  
import matplotlib.pyplot as plt 

#%%

censo2010 = pd.read_excel("censo2010.xlsx", skiprows = 14)
censo2022 = pd.read_excel("censo2022.xlsx", skiprows = 14)

## DATOS 2010
#-------------
posiciones_str2010=[]
lista_str2010 =[]
for i in range(len(censo2010)):
    v=censo2010.iloc[i,2]
    if (isinstance(v, str)& (v!=" Total")&(v!="Edad")):
        posiciones_str2010 = posiciones_str2010 + [i]
        lista_str2010 = lista_str2010 + [v]
    

#Buscamos posicion donde empieza el resumen, datos sin limpiar
pos_resumen_10 = 0
for i in range(len(censo2010)):
    v=censo2010.iloc[i,1]
    if (isinstance(v, str)& (v=="RESUMEN")):
        pos_resumen_10 = i
        

cant_hab2010=[]
for i in range(1,len(lista_str2010)):
    a = censo2010.iloc[ posiciones_str2010[i]- 2 ,5]
    cant_hab2010=cant_hab2010 + [a] 

cant_hab2010 = cant_hab2010 +  [censo2010.iloc[pos_resumen_10-2,5]] #le agregamos los habitantes de tierra del fuego


## DATOS 2022
#---------------
posiciones_str2022=[]
lista_str2022 =[]
for i in range(len(censo2022)):
    v=censo2022.iloc[i,2]
    if (isinstance(v, str)& (v!=" Total")&(v!="Edad")):
        posiciones_str2022 = posiciones_str2022 + [i]
        lista_str2022 = lista_str2022 + [v] 


#Buscamos posicion donde empieza el resumen
pos_resumen_22 = 0
for i in range(len(censo2022)):
    v=censo2022.iloc[i,1]
    if (isinstance(v, str)& (v=="RESUMEN")):
        pos_resumen_22 = i


cant_hab2022=[]
for i in range(1,len(lista_str2022)):
    a = censo2022.iloc[ posiciones_str2022[i]- 2 ,5]
    cant_hab2022=cant_hab2022 + [a]
    
cant_hab2022 = cant_hab2022 + [censo2022.iloc[pos_resumen_22-2,5]] 
#el procedimiento es igual al anterior, pero con distinto dataset


#GRAFICO POBLACION POR PROVINCIA EN 2010 VS 2022
#---------------

fig, ax = plt.subplots(figsize=(8, 10))
y = np.arange(len(lista_str2022))
ax.barh(y - 0.4/2, cant_hab2010, 0.4, label='2010', color="#4A4063")
ax.barh(y + 0.4/2, cant_hab2022, 0.4, label='2022', color='skyblue')
ax.set_yticks(y)
ax.set_yticklabels(lista_str2022, fontsize = 12)
ax.invert_yaxis()
ax.set_title('Poblacion por provincia (2010 y 2022)', fontsize = 18)
ax.legend()
fig.tight_layout()


#%%
#Nacimientos prematuros según provincia

nacimientos = pd.read_csv("nacimiento.csv")
provincia = pd.read_csv("provincia.csv")


nacimientos2010 = nacimientos.loc[nacimientos["anio"] == 2010, :].reset_index()
nacimientos2022 = nacimientos.loc[nacimientos["anio"] == 2022, :].reset_index()

#len(nacimientos2010) + len(nacimientos2022) == len(nacimientos) #verificacion

np.unique(nacimientos2010["tiempo_gestacion"]) #buscamos las categorias de "tiempo_gestacion" presentes en el dataset
prematuros2010Bool = (nacimientos2010["tiempo_gestacion"]!= "37 a 41") & (nacimientos2010["tiempo_gestacion"]!= "42 y más") 
prematuros2010 = nacimientos2010.loc[prematuros2010Bool, :].reset_index()

#np.unique(prematuros2010["tipo_gestacion"]) #verificacion


np.unique(nacimientos2022["tiempo_gestacion"])
prematuros2022Bool = (nacimientos2022["tiempo_gestacion"]!= "37 a 41") & (nacimientos2022["tiempo_gestacion"]!= "42 y más") 
prematuros2022 = nacimientos2022.loc[prematuros2022Bool, :].reset_index()
#np.unique(prematuros2022["tipo_gestacion"]) #verificacion


## Porcentaje de prematuros por provincia 2010
#---------------

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


## Porcentaje de prematuros por provincia 2022
#---------------

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


# GRAFICO PORCENTAJE DE PREMATUROS 
#---------------

prov = provincia['nombre']
x = np.arange(len(prov))

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(x - 0.3/2, lista_prov2010, 0.3,
       label='Porcentaje de prematuros en 2010', color='#4A4063')
ax.bar(x + 0.3/2, lista_prov2022, 0.3,
       label='Porcentaje de prematuros en 2022', color='skyblue')

ax.set_xticks(x)
ax.set_xticklabels(prov, rotation=45, ha='right', fontsize = 12)
ax.set_ylabel('Porcentaje de prematuros', fontsize = 12)
ax.set_title('Porcentaje de prematuros por provincia (2010 y 2022)', fontsize = 18)

ax.legend()
fig.tight_layout()
plt.show()

#%%

habitantes = pd.read_csv('habitante.csv')
nacimientos2022 = nacimientos.loc[nacimientos["anio"] == 2022, :].reset_index()


habitantes2022 = habitantes.loc[habitantes["anio"] == 2022, :].reset_index()
mujeres2022 = habitantes2022.loc[habitantes2022["sexo"] == 'mujer',:].reset_index()


# Lista de mujeres en edad fertil por provincia 
#------------

lista_fertiles22 = []
for v in np.unique(mujeres2022["id_provincia"]):
    mujeres_fertiles_por_prov = 0
    for i in range(len(mujeres2022)):
        grupo = mujeres2022["grupo_etario"][i]
        if (mujeres2022['id_provincia'][i] == v) & \
            ((grupo == '15 a 19') | (grupo == '20 a 24') | (grupo == '25 a 29') |
            (grupo == '30 a 34') | (grupo == '35 a 39') | (grupo == '40 a 44') |
            (grupo == '45 a 49')):
            mujeres_fertiles_por_prov += mujeres2022['cantidad'][i]
    lista_fertiles22.append(mujeres_fertiles_por_prov)
    

# Lista de madres por provincia    
#------------
      
lista_madres22 = []   
for v in np.unique(nacimientos2022['id_provincia']):
    madres_por_provincia = 0 
    for i in range(len(nacimientos2022)):
        if ((nacimientos2022['id_provincia'][i] == v) & (nacimientos2022["grupo_etario_madre"][i] != "Menor de 15")):
            madres_por_provincia += nacimientos2022['cantidad'][i]
    lista_madres22.append(madres_por_provincia)
    

# TASA DE FERTILIDAD CADA MIL 

tasa = ((np.array(lista_madres22))/(np.array(lista_fertiles22)))*1000    


#GRAFICO TASA VS NIVEL DE INSTRUCCIÓN DE LA MADRE

niveles = ['Hasta Primaria/C.EGB Completa','Secundaria/Polimodal Incompleta',
           'Secundario/Polimodal Completa y más']


# Armamos una tabla con la suma para cada provincia la cantidad de nacimientos separado por los niveles de educación de la madres
tabla = nacimientos2022.pivot_table(index='id_provincia', columns='nivel_instruccion_madre',
                       values='cantidad', aggfunc='sum', fill_value=0)[niveles]      

tabla_porcentaje = tabla.div(tabla.sum(axis=1), axis=0) * 100

# Reemplazamos el index por el nombre de la provincia
nombres = provincia.set_index('id')['nombre']
tabla_porcentaje.index = tabla_porcentaje.index.map(nombres)

fig, ax = plt.subplots(figsize=(16, 6))
tabla_porcentaje.plot(kind='bar', ax=ax, color=['#4A4063', 'skyblue', '#8FBC8F'], width=0.5)

ax.set_xlabel('')
ax.set_ylabel('Cantidad de nacimientos', fontsize = 12)
ax.set_title('Nivel de instrucción de la madre por provincia (2022)', fontsize = 18)
ax.legend(title='Nivel de instrucción', fontsize = 12)
plt.xticks(rotation=45, ha='right')
fig.tight_layout()
plt.show()

#%%
# GRAFICO TASA DE FECUNDIDAD POR PROVINCIA

tasa_por_prov = pd.DataFrame({'Provincia': nombres, 'tasa': tasa})
tasa_por_prov = tasa_por_prov.sort_values('tasa')

x = np.arange(len(tasa))

fig, ax = plt.subplots(figsize=(16, 6))
ax.bar(x,tasa_por_prov['tasa'] , color='skyblue')

ax.set_xticks(x)
ax.set_xticklabels(tasa_por_prov['Provincia'], rotation=45, ha='right', fontsize = 12)
ax.set_ylabel('Nacimientos cada 1000 mujeres de 15 a 49 años',fontsize = 12)
ax.set_title('Tasa de fecundidad por provincia, 2022',fontsize = 18)

fig.tight_layout()
plt.show()


#%%
# Bajo peso al nacer

bajo = nacimientos2022['peso_bebe'] == 'Menos de 2500 gramos'
np.unique(nacimientos2022['nivel_instruccion_madre'])

n1 = (nacimientos2022['nivel_instruccion_madre'] == 'Hasta Primaria/C.EGB Completa')
n2 = (nacimientos2022['nivel_instruccion_madre'] == 'Secundaria/Polimodal Incompleta')
n3 = (nacimientos2022['nivel_instruccion_madre'] == 'Secundario/Polimodal Completa y más')


tot1 = nacimientos2022[n1].groupby('id_provincia')['cantidad'].sum()
tot2 = nacimientos2022[n2].groupby('id_provincia')['cantidad'].sum()
tot3 = nacimientos2022[n3].groupby('id_provincia')['cantidad'].sum()


bajo1 = nacimientos2022[n1 & bajo].groupby('id_provincia')['cantidad'].sum()
bajo2 = nacimientos2022[n2 & bajo].groupby('id_provincia')['cantidad'].sum()
bajo3 = nacimientos2022[n3 & bajo].groupby('id_provincia')['cantidad'].sum()

bajo_peso = pd.DataFrame({'Hasta primaria completa': (bajo1 / tot1 * 100),
    'Secundaria incompleta': (bajo2 / tot2 * 100),
    'Secundaria completa y más': (bajo3 / tot3 * 100),}).reset_index()

bajo_peso = bajo_peso.merge(provincia, left_on='id_provincia', right_on='id')
bajo_peso = bajo_peso.sort_values('Hasta primaria completa')


# GRAFICO BAJO PESO AL NACER

x = np.arange(len(bajo_peso))
ancho = 0.27

fig, ax = plt.subplots(figsize=(16, 6))
ax.bar(x - ancho, bajo_peso['Hasta primaria completa'], ancho,
       label='Hasta primaria completa', color='#4A4063')
ax.bar(x, bajo_peso['Secundaria incompleta'], ancho,
       label='Secundaria incompleta', color='skyblue')
ax.bar(x + ancho, bajo_peso['Secundaria completa y más'], ancho,
       label='Secundaria completa y más', color='#8FBC8F')

ax.set_xticks(x)
ax.set_xticklabels(bajo_peso['nombre'], rotation=45, ha='right', fontsize=12)
ax.set_ylabel('% de nacimientos con bajo peso (< 2500 g)', fontsize=12)
ax.set_title('Bajo peso al nacer según nivel de instrucción de la madre por provincia 2022',fontsize=18)
ax.legend(title='Nivel de instrucción', fontsize=12)

fig.tight_layout()
plt.show()



# GRAFICO BRECHA EDUCATIVA PARA NACIMIENTOS DE BAJO PESO

d = bajo_peso.copy()
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
ax.set_yticklabels(d['nombre'].values, fontsize = 12)
ax.set_xlabel('% de nacimientos con bajo peso (< 2500 g)', fontsize = 12)
ax.set_title('Bajo peso al nacer según instrucción de la madre por provincia (2022)',fontsize = 18)
ax.legend()
ax.grid(axis='x', alpha=0.3)

fig.tight_layout()
plt.show()

#%%
centros_salud = pd.read_csv('centro_de_salud.csv')
por_depto = centros_salud.groupby(['provincia_id', 'departamento_id']).size().reset_index(name='cantidad')


datos = []
nombres = []
for v in np.unique(por_depto['provincia_id']):
    datos.append(por_depto[por_depto['provincia_id'] == v]['cantidad'].values)
    nombres.append(provincia[provincia['id'] == v]['nombre'].values[0])


#GRAFICO ESTABLECIMIENTOS DE SALUD

#Elegimos escala logaritmica para que se vea mejorr
fig, ax = plt.subplots(figsize=(16, 7))
ax.boxplot(datos)

ax.set_yscale('log')

ax.set_xticks(np.arange(1, len(nombres) + 1))
ax.set_xticklabels(nombres, rotation=45, ha='right', fontsize=12)
ax.set_ylabel('Establecimientos de salud por departamento (escala log)',fontsize=12)
ax.set_title('Distribución de establecimientos de salud por departamento según provincia',fontsize=18)
ax.grid(axis='y', alpha=0.3)

fig.tight_layout()
plt.show()



