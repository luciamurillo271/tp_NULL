# tp_NULL
Fuentes
1. Población según censo 2010: cantidad de habitantes en base a provincia, edad, sexo, tipo de cobertura de salud. Obtenido por cruce múltiple en la categoría de población, y tomando como variables “cobertura de salud”, “edad” y “sexo”; considerando la provincia como corte de área. 
2. Población según censo 2022: cantidad de habitantes en base a provincia, edad, sexo, tipo de cobertura de salud. Obtenido por cruce múltiple en la categoría de población, y tomando como variables “cobertura de salud”, “edad” y “sexo registrado al nacer”; considerando la provincia como corte de área.
3. Nacidos vivos registrados en la República Argentina en los años 2010 y 2022 en base a provincia de residencia de la madre, tipo de parto, sexo, edad de la madre, tiempo de gestación, nivel de instrucción de la madre y peso al nacer. Cada uno contiene datos agregados: cada fila representa una combinación de atributos y la columna CUENTA indica la cantidad de nacidos vivos correspondiente. Notar que el formato de los archivos no es homogéneo
4. Establecimientos de salud asentados en el registro federal (REFES) Abril 2022 en base a provincia y departamento

Instrucciones python
1. pd.read_excel(sheet_name=’...’, skiprows=): comando para leer archivos tipo .xlsx, el atributo skiprows permite saltear las primeras n líneas del archivo. Requiere tener la biblioteca openpyxl.
2. pd.read_csv(sep=, encoding=): comando para leer archivos tipo .csv, los atributos sep y encoding permiten indicar el separador de campos y la codificación de caracteres del archivo.
3. df.dropna(): Elimina las tuplas con valores nulos en alguna de las columnas del dataframe dado.
4. df.to_csv(): Exporta un dataframe como archivo .csv.
5. fig.savefig(‘nombre.png’): Exporta una figura de matplotlib como png.
6. np.where(): Permite reemplazar los valores de una columna de un dataframe que cumplen con una condición dada.
