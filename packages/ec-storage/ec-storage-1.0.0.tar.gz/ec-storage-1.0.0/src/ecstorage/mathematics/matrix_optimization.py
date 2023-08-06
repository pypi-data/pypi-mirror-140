import numpy as np
import math

# (numpy array格式)稠密矩阵 转 稀疏矩阵
def sparse(data):
    
    if type(data) == list:
        data = np.array(data,ndmin=2)
    elif data.ndim == 1:
        data = np.array(data,ndmin=2)
        data = data.transpose()
    sparse_matrix = []

    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if data[i][j] != 0:
                sparse_matrix.append((i,j,data[i][j]))
    return sparse_matrix

'''
(numpy array格式)稀疏矩阵 转 稠密矩阵
注:该函数只支持一行转为结果为一行的稠密矩阵
只支持以行数小的在前面这种格式的转换,
例如支持[(0,0,0), (1, 0, 0)], 不支持[(1,0,0), (0,0,0)],
即输入稀疏矩阵的排序规则需要符合order by row,col
'''
def dense(data):
    dense_matrix = np.array([])
    tmp = []
    for i in range(len(data)):
            tmp.append(data[i][2])
    dense_matrix = np.insert(tmp, 0, values=dense_matrix, axis=0)
    return dense_matrix

'''
将元素全为MatrixEntrytoArray类型的 RDD 转为 list
'''
def MatrixEntrytoArray(data):
    data = data.collect()
    data_new = []
    for i in range(len(data)):
        # list(map(int,str(data[i]).replace('MatrixEntry','')[1:-1].split(',') ))   #这样float型转换不了
        
        xyz = str(data[i]).replace('MatrixEntry','')[1:-1].split(',')
        xyz = [intorfloat(i) for i in xyz]          #强制int型
        data_new.append( tuple(xyz) ) 
    return data_new
'''
字符串转为int/float/double类型,优先int
输入:
    data(字符串类型)
输出:
    data(int/float型)
'''
def intorfloat(data):
    if type(data) == int:
        data = int(data)
    elif type(data) == float and int(data) - data == 0:
        data = int(data)
    else:
        data = float(data)
    return data

'''
取list中每个元组的首个数值
输入:
    data(list格式,元素为元组)
输出:
    data(list格式,元素为值)
'''
def tuplefirstvalue(data):
    data_new = []
    for i in range(len(data)):
        data_new.append( intorfloat(data[i][2]) )

    return data_new

'''
结果近似为整数的,返回整数

输入:
    data (list格式)
输出:
    data (list格式)
'''
def approximateintegertointeger(data):
    for i in range(len(data)):
        if abs( data[i] - round(data[i]) ) < 10**-8:
            data[i] = int( round(data[i]) )
    return data


'''
nan 替换成 None
输入:
    data (list格式)
输出:
    data (list格式)
'''
def nanreplce(data):
    for i in range(len(data)):

        # None 不能用math.isnan()判断
        try:
            if math.isnan(data[i]):     
                data[i] = None
        except:
            continue
        else:
            continue
        
    return data