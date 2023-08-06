#!/usr/bin/env python
# coding: utf-8

import os
import pprint
import pandas as pd
from collections import OrderedDict


def get_parameters():
    # Read Data
    try:
        df_8468 = pd.read_excel(
            io=os.path.join(os.path.dirname(__file__), 'data', 'tab_dec_8468.xlsx'),
            sheet_name='dec_8468',
            index_col=0
        )
    except Exception as e:
        #print(e, '\n')
        #print('Read table from GitHub')
        df_8468 = pd.read_excel(
            io='https://raw.githubusercontent.com/gaemapiracicaba/norma_dec_8468-76/main/src/normas/data/tab_dec_8468.xlsx',
            sheet_name='dec_8468',
            index_col=0
        )

    # Filter only quality
    df_8468 = df_8468.loc[(df_8468['tipo_padrao'] == 'qualidade')]
    #print(df_8468.head())

    # Classes
    list_classes = list(set(df_8468['padrao_qualidade']))
    list_classes = [x for x in list_classes if pd.notnull(x)]
    list_classes.sort()    

    return df_8468, list_classes


def filter_by_classe(df_8468, classe):
    # Filter dataframe by Classe
    df_8468 = df_8468.loc[(df_8468['padrao_qualidade'] == classe)]

    # Parâmetros
    list_parametros = list(set(df_8468['parametro_descricao']))
    list_parametros = [x for x in list_parametros if pd.notnull(x)]
    list_parametros.sort()    
    return df_8468, list_parametros


def filter_by_parameters(df_8468, parametro):
    # Filter dataframe by Parametro
    df_8468 = df_8468.loc[(df_8468['parametro_descricao'] == parametro)]

    # Check and Get Results
    if len(df_8468) == 1:
        dict_8468 = df_8468.to_dict(orient='records')[0]
        dict_8468 = OrderedDict(sorted(dict_8468.items(), key=lambda x: df_8468.columns.get_loc(x[0])))
        return dict_8468
    else:
        return 'erro'


def set_type_desconformidade(dict_8468):
    if pd.isnull(dict_8468['valor_minimo_permitido']) & pd.notnull(dict_8468['valor_maximo_permitido']):
        #print('Parâmetro só tem "valor máximo". Caso o valor medido esteja acima, é amostra desconforme!')
        tipo_8486 = 'acima>desconforme'

    elif pd.notnull(dict_8468['valor_minimo_permitido']) & pd.isnull(dict_8468['valor_maximo_permitido']):
        #print('Parâmetro só tem "valor mínimo". Caso o valor medido esteja abaixo, é amostra desconforme!')
        tipo_8486 = 'abaixo>desconforme'

    elif pd.notnull(dict_8468['valor_minimo_permitido']) & pd.notnull(dict_8468['valor_maximo_permitido']):
        #print('Parâmetro tem "valor mínimo" e "valor máximo". Caso o valor medido acima ou abaixo, é amostra desconforme!')
        tipo_8486 = 'abaixo_acima>desconforme'

    elif pd.isnull(dict_8468['valor_minimo_permitido']) & pd.isnull(dict_8468['valor_maximo_permitido']):
        #print('Erro!')
        tipo_8486 = 'erro'
    else:
        print('Erro!')
        #tipo_8486 = 'erro'

    return tipo_8486


def evaluate_result(valor, dict_8468):
    # Get type
    tipo_8486 = set_type_desconformidade(dict_8468)

    # Evaluate type
    if tipo_8486 == 'acima>desconforme':
        if valor > dict_8468['valor_maximo_permitido']:
            result_8468 = 'desconforme'
        else:
            result_8468 = 'conforme'

    elif tipo_8486 == 'abaixo>desconforme':
        if valor < dict_8468['valor_minimo_permitido']:
            result_8468 = 'desconforme'
        else:
            result_8468 = 'conforme'

    elif tipo_8486 == 'abaixo_acima>desconforme':
        if dict_8468['valor_minimo_permitido'] <= valor <= dict_8468['valor_maximo_permitido']:
            result_8468 = 'conforme'
        else:
            result_8468 = 'desconforme'

    else:
        result_8468 = 'erro'

    return result_8468

