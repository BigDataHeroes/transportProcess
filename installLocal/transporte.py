# -*- coding: utf-8 -*-
"""Transporte.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Cfh_nLsCQGHLwSSTSMpz-3mLUHZOuBuU

# Análisis exploratorio de datos de transporte
"""

import pandas as pd
from hdfs3 import HDFileSystem

import sys


inputMetro=sys.argv[1]
inputEMT=sys.argv[2]
ouPath=sys.argv[3]
baseMadridG=sys.argv[4]
baseBarriosG=sys.argv[5]
ouPathAgg=sys.argv[6]

hdfs = HDFileSystem(host='bdhKC', port=9000)
with hdfs.open(inputMetro) as f:
    metro = pd.read_csv(f)
metro['TIPOTRANSPORTE'] = 'Metro'

with hdfs.open(inputEMT) as f:
    autobus = pd.read_csv(f)
autobus['TIPOTRANSPORTE'] = 'Autobus'

transporte = pd.concat([metro, autobus], ignore_index=True)

transporte = transporte.loc[:,['BARRIO', 'CODIGOPOSTAL', 'DENOMINACION', 'DISTRITO', 'LATITUD', 'LONGITUD', 'TIPOTRANSPORTE']]

nas_dictionary = {"columns":[], "nas_count":[]}
for column in transporte.columns:
    nas_dictionary["columns"].append(column)
    nas_dictionary["nas_count"].append(len(transporte[column])-transporte[column].count())
nas_dictionary
nas_dataframe = pd.DataFrame(nas_dictionary)



import json
import numpy as np
from shapely.geometry import shape, Point

with hdfs.open(baseMadridG) as f:
    js = json.load(f)
    
for index, row in transporte.iterrows():
    point = Point(row['LONGITUD'], row['LATITUD'])
    encontrado = False
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            transporte.loc[index, 'CODIGOPOSTAL'] = float(feature['properties']['COD_POSTAL'])
            encontrado = True
            break
    if not encontrado:
      transporte.loc[index, 'CODIGOPOSTAL'] = np.nan

with hdfs.open(baseBarriosG) as f:
    js = json.load(f)
for index, row in transporte.iterrows():
    point = Point(row['LONGITUD'], row['LATITUD'])
    encontrado = False
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            if feature['properties']['CODBAR'] == '093':
              print(transporte.loc[index])
              print(feature)
            transporte.loc[index, 'BARRIO']=float(feature['properties']['CODBAR'])
            transporte.loc[index, 'DISTRITO']=float(feature['properties']['CODDIS'])
            transporte.loc[index, 'BARRIO_NOMBRE']=str(feature['properties']['NOMBRE'])
            transporte.loc[index, 'DISTRITO_NOMBRE']=str(feature['properties']['NOMDIS'])
            encontrado = True
            break
            
    if not encontrado:
        transporte.loc[index, 'BARRIO'] = np.nan
        transporte.loc[index, 'DISTRITO'] =np.nan
        transporte.loc[index, 'BARRIO_NOMBRE'] = np.nan
        transporte.loc[index, 'DISTRITO_NOMBRE'] = np.nan


transporte = transporte.dropna()

transporte.loc[:, 'DENOMINACION'] = transporte.DENOMINACION.replace("\'", "", regex=True)

"""## Guardar datos limpios"""

with hdfs.open(ouPath,'wb') as f:
    transporte.to_csv(f, sep=",")

"""## Agregacion de datos"""

datos_limpios = transporte

datos_limpios.info()

grouped = datos_limpios.groupby(by=['DISTRITO_NOMBRE','DISTRITO','BARRIO_NOMBRE', 'BARRIO', 'TIPOTRANSPORTE'])

import numpy as np
datos_agregados = grouped.agg({
                      'DENOMINACION':'count'
                  })
transporte_agregado = datos_agregados.unstack().reset_index()
transporte_agregado.columns = [['DISTRITO_NOMBRE',
 'DISTRITO',
 'BARRIO_NOMBRE',
 'BARRIO',
 'Autobus',
 'Metro']]
transporte_agregado = transporte_agregado.rename(columns={
                      'DISTRITO_NOMBRE':'Distrito_Nombre',
                      'DISTRITO': 'Distrito',
                      'BARRIO_NOMBRE':'Barrio_Nombre',
                      'BARRIO':'Barrio'
                  })



"""## Guardar datos agregados"""
with hdfs.open(baseBarriosG,'wb') as f:
    transporte_agregado.to_csv(f, sep=",")
