# -*- coding: utf-8 -*- 
"""tabela_vitoria_projeto_final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OJ7IptH2UqIevQIpTPlVqOToW4PNhDXR

INSTALAÇÃO DAS BIBLIOTECAS
"""

pip install gcsfs

pip install pandera

"""DECLARAÇÃO DAS LIBS"""

import pandas as pd
import os
import numpy as np
from google.cloud import storage
import pandera as pa

"""CONECTANDO COM O BUCKET"""

#CONFIGURANDO DA CHAVE DE SEGURANCA (Enviada com o projeto)

serviceAccount = '/content/squad-7-economia-5ec84694df36.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = serviceAccount

#Configurações Google Cloud Storage
client = storage.Client()
bucket = client.get_bucket('economy-squad-7')
bucket.blob('gs://economy-squad-7/Tabelas escolaridade/csv/Tabelas escolaridade_RM 63200 Vitória - Base UDH 2000_2010.xlsx - Sheet1.csv')
path = 'gs://economy-squad-7/Tabelas escolaridade/csv/Tabelas escolaridade_RM 63300 Rio de Janeiro - Base UDH 2000_2010.xlsx - Sheet1.csv'

"""EXTRAÇÃO DOS DADOS"""

df = pd.read_csv(path, sep=',')

"""PRÉ-ANÁLISE"""

df

#Tam. do DF
df.shape

#Visualiza valores unicos na coulna
pd.unique(df[''])

df.dtypes

df.count()

#criando um novo df com as colunas que importam
df_novo = df.loc[:, ['ANO', 'NOME_UDH', 'NOME_MUN', 'NOME_RM', 'NOME_UF', 'GINI',\
                     'I_ESCOLARIDADE', 'IDHM', 'IDHM_E', 'IDHM_L', 'IDHM_R', 'P_AGRO',\
                     'P_COM', 'P_CONSTR', 'P_EXTR', 'P_SERV', 'P_SIUP', 'P_TRANSF',\
                     'CPR', 'EMP', 'P_FORMAL', 'TRABCC', 'TRABPUB', 'TRABSC',\
                     'PEA18M', 'PESORUR', 'PESOTOT', 'PESOURB', 'PIA18M', 'R1040',\
                     'R2040', 'RDPC', 'RENOCUP', 'TRABCC', 'TRABPUB', 'THEILtrab', 'TRABSC',]]

df = df_novo

df.shape

df.dtypes



"""TRANSFORMAÇÕES (LIMPEZAS ETC)"""

#Backup local(M.RAM) do df
dfback = df.copy()

#Verificando dados nulos, ausentes etc
df.isna().sum()

GINInulo = df.GINI.isna()
df.loc[GINInulo]

#Dropando os 9 registros nulos
df_sem_nulos = df.dropna()

df = df_sem_nulos

df.isna().sum()

df.shape

#Enviando o novo df pro bucket
df.to_csv('gs://economy-squad-7/Tabelas escolaridade/filtradas/Tabela Rio de Janeiro- filtrada.csv',index=False)

df.dtypes

df

df['PESORUR'] = df['PESORUR'].astype(int)
df['PESOTOT'] = df['PESOTOT'].astype(int)
df['PESOURB'] = df['PESOURB'].astype(int)

df.dtypes