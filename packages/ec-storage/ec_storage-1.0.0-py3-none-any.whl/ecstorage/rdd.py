import numpy as np
from pyspark.mllib.linalg.distributed import *
from ecstorage.mathematics.generator_matrix import generator
from ecstorage.mathematics.matrix_optimization import *

'''
把数值修改成None
输入:
    check_data: 包含校验块的缺失数据(np.array)
    loss_idx:   缺失数据的索引(np.array)
    m:          校验块个数
输出:
    check_data: 相比输入更多缺失的数据（缺失个数为m）
    loss_idx:   输出check_data缺失数据的索引
'''
def none_enough(check_data,loss_idx,m):
    loss_idx = loss_idx.tolist()
    # check_data.filter(lambda data:data.collect()[i][0] != None for i in range(len(loss_idx))  )
    i = 0
    while len(loss_idx) < m:
        check_data[i] = None
        loss_idx = np.where(np.array(check_data) == None)[0]
        i = i + 1
    return check_data,loss_idx

'''
生成校验块
输入:
    sc:     SparkContext
    data:   输入数据 (rdd格式数据)
    m:      校验块个数 (python int型数据)
输出:
    generator_matrix: 生成矩阵
    generator_matrix.dot(data): 数据块+校验块
'''
def reedsolomon(sc,data,m,generator_matrix_case = 'cauchy'):
    data = sc.parallelize( sparse(np.array(data.collect() ))  )
    
    k = data.count()

    # 产生生成矩阵
    generator_matrix = np.array(generator(k,m))

    generator_matrix = sc.parallelize(sparse(generator_matrix))     #将稠密矩阵转换为稀疏矩阵并创建RDD

    data = CoordinateMatrix(data).toBlockMatrix()
    generator_matrix = CoordinateMatrix(generator_matrix).toBlockMatrix()
    check_block = generator_matrix.multiply(data).toCoordinateMatrix().entries.collect()    # MatrixEntry格式
    
    # 格式转换
    check_block = sc.parallelize(check_block[-m:])
    check_block = MatrixEntrytoArray(check_block)   # 元素全为MatrixEntry的RDD 转 list
    check_block = sc.parallelize(dense(np.array(check_block)).tolist())   #稀疏矩阵格式 转 稠密矩阵格式
    
    return check_block

'''
恢复数据
输入:
    loss_data:
    check_block:
    generator_matrix_case: 生成矩阵采用的方法(缺省值),默认是 'cauchy'
    arraytype:  数组计算类型(缺省值),默认是 'int'（浮点数计算可能结果错误）
    outtype: 输出类型(缺省值),默认是list类型
'''
def verify(sc,loss_data,check_block,generator_matrix_case = 'cauchy',arraytype = 'int',outtype='list'):
    loss_data = sc.parallelize( sparse(np.array(loss_data.collect() ))  )

    if arraytype == 'int':
        arraytype = np.int
    else:
        arraytype = np.float32

    k = loss_data.count()
    m = check_block.count()

    # 生成矩阵
    generator_matrix = np.array(generator(k,m)).astype(arraytype)

    loss_data = dense(loss_data.collect())

    check_data = np.array(loss_data).tolist() + np.array(check_block.collect()).tolist()

    # nan替换成None
    check_data = nanreplce(check_data)
    loss_idx = np.where(np.array(check_data) == None)[0]

    # 如果None不够就删掉一些好让后续生成矩阵是方阵求逆
    check_data,loss_idx = none_enough(np.array(check_data),loss_idx,m)
            
    # 删除生成矩阵(generator_matrix) 中对应缺失数据的行 
    generator_matrix = np.delete(generator_matrix,loss_idx, axis = 0)

    # 删除数据中值为None的数据
    check_data = np.delete(check_data,loss_idx, axis = 0).astype(arraytype)
    check_data = sc.parallelize(sparse(check_data))

    # 求生成矩阵逆矩阵并处理数据格式
    generator_matrix  = sparse( np.linalg.inv(generator_matrix) )       #生成矩阵逆矩阵（稀疏矩阵格式）
    generator_matrix = sc.parallelize(  generator_matrix  )     #创建RDD

    # 矩阵计算
    generator_matrix = CoordinateMatrix(generator_matrix).toBlockMatrix()
    check_data = CoordinateMatrix(check_data).toBlockMatrix()

    recover_data = generator_matrix.multiply(check_data).toCoordinateMatrix().entries.collect()

    recover_data = tuplefirstvalue( MatrixEntrytoArray(sc.parallelize(recover_data)) )

    # 如果值为近似整数,则转为整数
    if arraytype == np.int:
        recover_data = approximateintegertointeger(recover_data)
    recover_data = sc.parallelize(recover_data)

    return recover_data