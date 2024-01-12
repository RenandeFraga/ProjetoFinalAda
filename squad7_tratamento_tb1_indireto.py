# -*- coding: utf-8 -*- 
"""Squad7_tratamento_tb1_indireto.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CNMva9cpdjoUVLzojSvbRxHvrs1fIpLC

#Instalando bibliotecas e configurando conector do bucket
"""

!pip install pyspark

!pip install gcsfs

!pip install google-cloud-storage

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from pyspark.sql.functions import when, regexp_replace
from google.cloud import storage
import os
warnings.filterwarnings("ignore")

#CONFIGURAR A CHAVE
serviceAccount = '/content/squad-7-economia-5ec84694df36.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = serviceAccount

#CONFIGURAR A VARIÁVEL DE AMBIENTE (SESSÃO)
spark = (SparkSession.builder
                     .master('local')
                     .appName('projeto_final_teste')
                     .config('spark.ui.port', '4050')
                     .config("spark.jars", 'https://storage.googleapis.com/hadoop-lib/gcs/gcs-connector-hadoop2-latest.jar')
                     .getOrCreate()
)

df = (spark.read
         .format('csv')
         .option('delimiter', ';')
         .option('header', 'true')
         .option('inferschema', 'true')
         .load('gs://economy-squad-7/tratados/op_indiretas_auto_tratado.csv')
)

"""#Analise inicial do DataSet"""

df.show()

df.printSchema()

print(f'({df.count()}, {len(df.columns)})')

"""#Alterações iniciais

##Identificando Nulos
"""

df.select([F.count(F.when(F.col(c).isNull(), c)).alias(c) for c in df.columns]).show()

#Dropando colunas com valores nulos
df = df.dropna(how='any')

"""##Identificando colunas duplicadas"""

sem_duplicados = df.drop_duplicates().count()
qtd_registros = df.count()
total_duplicados = qtd_registros - sem_duplicados
print(total_duplicados)

#Drop nas colunas duplicadas
df = df.drop_duplicates()

print(f'({df.count()}, {len(df.columns)})')

"""##Dropando colunas que não vão ser utilizadas na analise"""

df = df.drop(F.col('cpf_cnpj'), F.col('municipio_codigo'), F.col('cnpj_do_agente_financeiro'),F.col('subsetor_cnae_codigo'))

"""#Analisando coluna por coluna"""

df.printSchema()

"""##Coluna valor_desembolsado_reais estava como sting, vamos mudar para interger"""

df.select('valor_desembolsado_reais').distinct().orderBy('valor_desembolsado_reais').collect()

df = df.withColumn('valor_desembolsado_reais',
                   F.when(F.col('valor_desembolsado_reais').rlike('^[0-9]+$'),
                          F.col('valor_desembolsado_reais').cast('integer'))
                    .otherwise(F.regexp_replace(F.col('valor_desembolsado_reais'), '[,.]', '').cast('integer')))

df = df.withColumn('valor_desembolsado_reais', regexp_replace(F.col('valor_desembolsado_reais').cast('string'), r'\d$', '').cast('integer'))

df.printSchema()

#Verificando se apareceram novos nulos
df.filter(df.valor_desembolsado_reais.isNull()).show()

df = df.dropna(how='any')

df.filter(df.valor_desembolsado_reais.isNull()).show()

"""##Coluna 'juros' também estava como String, então sera alterada para float"""

df = df.withColumn('juros',
                   F.when(F.col('juros').rlike('^[0-9]+$'),
                          F.col('juros').cast('float'))
                    )

df.select('juros').distinct().orderBy('juros').collect()

"""#Identificando nomes repetidos ou com inconsistências ortográficas

##Verificando valores da coluna subsetor_bndes
"""

df.groupBy(F.col('subsetor_bndes')).agg(F.count('*').alias('contagem')).orderBy(F.col('contagem').desc()).show(truncate=False)

#USANDO REGEX PARA COLOCAR VALOR ÚNICO EM OUTRAS PARA IGUALAR A OUTROS
df = df.withColumn("subsetor_bndes", when(df.subsetor_bndes == "OUTRAS", "OUTROS").otherwise(df.subsetor_bndes))

"""##Verificando valores da coluna fonte_de_recursos_desembolsos"""

fonte_de_recurso_desembolsos_unicos = df.select('fonte_de_recurso_desembolsos').distinct()

fonte_de_recurso_desembolsos_unicos.orderBy(fonte_de_recurso_desembolsos_unicos["fonte_de_recurso_desembolsos"].desc()).show(truncate=False)

"""fonte_de_recursos_desembolsos não apresentou incongruências

---

##Verificando valores da coluna custo_financeiro
"""

custo_financeiro_unicos = df.select('custo_financeiro').distinct()

custo_financeiro_unicos.orderBy(custo_financeiro_unicos["custo_financeiro"].desc()).show(truncate=False)

"""custo_financeiro não apresentou incongruências

---

##Verificando valores da coluna modalidade_de_apoio
"""

modalidade_de_apoio_unicos = df.select('modalidade_de_apoio').distinct()

modalidade_de_apoio_unicos.orderBy(modalidade_de_apoio_unicos["modalidade_de_apoio"].desc()).show(truncate=False)

"""Todos os valores da coluna contam como REEMBOLSÁVEL

##Verificando valores da coluna forma_de_apoio
"""

forma_de_apoio_unicos = df.select('forma_de_apoio').distinct()

forma_de_apoio_unicos.orderBy(forma_de_apoio_unicos["forma_de_apoio"].desc()).show(truncate=False)

"""Todos os valores da coluna contam como INDIRETA

## Verificando valores da coluna produto
"""

produto_unicos = df.select('produto').distinct()

produto_unicos.orderBy(produto_unicos["produto"].desc()).show(truncate=False)

"""A coluna produto não apresenta incongruências

##Verificando valores da coluna instrumento_financeiro
"""

instrumento_financeiro_unicos = df.select('instrumento_financeiro').distinct()

instrumento_financeiro_unicos.orderBy(instrumento_financeiro_unicos["instrumento_financeiro"].desc()).show(truncate=False)

"""A coluna instrumento_financeiro não apresenta incongruências

##Verificando valores da coluna inovacao
"""

inovacao_unicos = df.select('inovacao').distinct()

inovacao_unicos.orderBy(inovacao_unicos["inovacao"].desc()).show(truncate=False)

"""A coluna inovacao não apresenta incongruências

##Verificando valores da coluna area_operacional
"""

area_operacional_unicos = df.select('area_operacional').distinct()

area_operacional_unicos.orderBy(area_operacional_unicos["area_operacional"].desc()).show(truncate=False)

"""Todos os valores da coluna contam como AREA DE OPERACOES E CANAIS DIGITAIS

##Verificando valores da coluna setor_cnae
"""

setor_cnae_unicos = df.select('setor_cnae').distinct()

setor_cnae_unicos.orderBy(setor_cnae_unicos["setor_cnae"].desc()).show(truncate=False)

"""A coluna setor_cnae não apresenta incongruências

##Verificando valores da coluna subsetor_cnae_agrupado
"""

subsetor_cnae_agrupado_unicos = df.select('subsetor_cnae_agrupado').distinct()

subsetor_cnae_agrupado_unicos.orderBy(subsetor_cnae_agrupado_unicos["subsetor_cnae_agrupado"].desc()).show(truncate=False)

"""A coluna subsetor_cnae_agrupado não apresenta incongruências

##Verificando valores da coluna subsetor_cnae_nome
"""

subsetor_cnae_nome_unicos = df.select('subsetor_cnae_nome').distinct()

subsetor_cnae_nome_unicos.orderBy(subsetor_cnae_nome_unicos["subsetor_cnae_nome"].desc()).show(truncate=False)

"""A coluna subsetor_cnae_nome não apresenta incongruências

##Verificando valores da coluna porte_do_cliente
"""

porte_do_cliente_unicos = df.select('porte_do_cliente').distinct()

porte_do_cliente_unicos.orderBy(porte_do_cliente_unicos["porte_do_cliente"].desc()).show((1000), truncate=False)

"""A coluna porte_do_cliente não apresenta incongruências

##Verificando valores da coluna natureza_do_cliente
"""

natureza_do_cliente_unicos = df.select('natureza_do_cliente').distinct()

natureza_do_cliente_unicos.orderBy(natureza_do_cliente_unicos["natureza_do_cliente"].desc()).show((1000), truncate=False)

"""A coluna natureza_do_cliente não apresenta incongruências

##Verificando valores da coluna instituicao_financeira_credenciada
"""

instituicao_financeira_credenciada_unicos = df.select('instituicao_financeira_credenciada').distinct()

instituicao_financeira_credenciada_unicos.orderBy(instituicao_financeira_credenciada_unicos["instituicao_financeira_credenciada"].desc()).show((1000), truncate=False)

"""A coluna instituicao_financeira_credenciada não apresenta incongruências

##Verificando valores da coluna situacao_da_operacao
"""

situacao_da_operacao_unicos = df.select('situacao_da_operacao').distinct()

situacao_da_operacao_unicos.orderBy(situacao_da_operacao_unicos["situacao_da_operacao"].desc()).show((1000), truncate=False)

"""A coluna situacao_da_operacao não apresenta incongruências

#Importando o tratado para o bucket
"""

df.repartition(1).write.format("csv").option("header", "true").option('delimiter', ';').option('inferschema', 'true').mode("overwrite").save("gs://economy-squad-7/tratados/operacoes_tratado2.csv")