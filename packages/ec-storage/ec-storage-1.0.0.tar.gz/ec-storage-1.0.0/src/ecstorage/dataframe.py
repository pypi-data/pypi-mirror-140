import numpy as np
from pyspark.sql import *
from pyspark.mllib.linalg.distributed import *
from ecstorage.mathematics.generator_matrix import generator
from ecstorage.mathematics.matrix_optimization import *
from ecstorage import rdd

# 有空再用原生的dataframe写
def reedsolomon(sc,data,m,generator_matrix_case = 'cauchy'):

    data = sc.parallelize( list(data.select(data.columns[0]).toPandas()[str(data.columns[0])]) )

    check_block = rdd.reedsolomon(sc,data,m,generator_matrix_case)  # RDD格式

    row = Row("check_block")     #列名
    check_block = check_block.map(row).toDF()

    return check_block


def verify(sc,loss_data,check_block,generator_matrix_case = 'cauchy',arraytype = 'int',outtype='list'):

    loss_data = sc.parallelize( list(loss_data.select(loss_data.columns[0]).toPandas()[str(loss_data.columns[0])]) )
    check_block = sc.parallelize( list(check_block.select(check_block.columns[0]).toPandas()[str(check_block.columns[0])]) )

    recover_data = rdd.verify(sc,loss_data,check_block,generator_matrix_case,arraytype,outtype)

    row = Row("data")     #列名
    recover_data = recover_data.map(row).toDF()

    return recover_data