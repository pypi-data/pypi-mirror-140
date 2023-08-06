# EC
[EC存储（ec-storage）](https://pypi.org/project/ec-storage/)

## file

> 源码文件目录（src/ecstorage）：
>
> - __init\_\_.py                        
> - mathematics                 数学函数
>      - __init\_\_.py				
>      - galois.py              伽罗华域运算
>      - generator_matrix.py    生成矩阵 
>      - matrix_optimization.py   矩阵优化
> - list.py           list格式计算
> - rdd.py          rdd格式计算
> - dataframe.py   dataframe格式计算（开发中）

## install

```shell
pip install ec-storage
```



## manual

### 导入模块

<kbd>ec-storage</kbd>提供了适合三种数据格式的计算方式，分别为`list`、`rdd`、`dataframe`（开发中），根据需要选择其中一种即可

```python
import ecstorage.list as ec
import ecstorage.rdd as ec
import ecstorage.dataframe as ec
```

> 为了方便后续的书写，建议将导入ec-storage的list或rdd或dataframe命名为ec，如上述代码块所示

### 生成校验块

```python
check_block = ec.reedsolomon(sc,data,m,generator_matrix)
```

> 这个ec需要与上面选择的接口一致（选择<kbd>list</kbd>接口则可以去掉sc这个参数）

### 恢复数据

```python
recover_data = ec.verify(data,check_block)
```

> recover_data 与 data 相同

### demo

#### list格式

```python
# 本地文件夹测试导入
# import sys
# sys.path.append("/Users/caiwei/Documents/code/EC-dev/src")

# 导入模块
import ecstorage.list as ec
import numpy as np

m = 3                       #选择校验块个数
generator_matrix = 'vander' #生成矩阵选择范德蒙德矩阵

data = [1, 0, 0, 8, 6]			#list格式数据
k = len(data)

check_block = ec.reedsolomon(data,m,generator_matrix)	#生成校验块(list格式)

# 测试（数据缺失个数+校验块缺失个数 <= m）
data[0] = None          # 缺失数据
data[1] = None
check_block[1] = None		#校验块也可以缺失
print(data)

# 恢复数据
recover_data = ec.verify(data,check_block,generator_matrix)	#恢复数据(list格式)
print(recover_data)		#[1, 0, 0, 8, 6]
```

#### RDD格式

```python
# #本地文件夹测试导入
# import sys
# sys.path.append("/Users/caiwei/Documents/code/EC-dev/src")

# #统一python版本(有多个python版本的情况下)
# import os
# os.environ["PYSPARK_PYTHON"]="/Users/caiwei/opt/anaconda3/bin/python"
# os.environ["PYSPARK_DRIVER_PYTHON"]="/Users/caiwei/opt/anaconda3/bin/python"

# 导入必要的模块
import ecstorage.rdd as ec
from pyspark import SparkContext
from pyspark.mllib.linalg.distributed import *
from pyspark.sql import SparkSession
from ecstorage.mathematics.matrix_optimization import sparse
import numpy as np

m = 3                       #校验块个数
generator_matrix = 'vander' #生成矩阵选择范德蒙德矩阵

# 创建spark session
sc = SparkContext()
spark = SparkSession(sc)

# 数据
data = np.arange(1,6,1)
data = sc.parallelize(data)	#数据转为rdd格式

# 生成校验块
check_block = ec.reedsolomon(sc,data,m,generator_matrix)

# 测试（数据缺失个数+校验块缺失个数 <= m）
data = list(np.arange(1,6,1))
data[0] = None          # 缺失数据（缺失个数小于等于m）
data[1] = None
# data[2] = None


# 也可以是校验块有缺失数据
check_block = check_block.collect()
check_block[0] = None
check_block = sc.parallelize(check_block)

# 恢复数据
recover_data = ec.verify(sc,data,check_block,generator_matrix)  
print(recover_data.collect())

```

#### dataframe格式

```python

# 文件夹测试导入
import sys
sys.path.append("/Users/caiwei/Documents/code/EC-dev/src")

# 导入模块
import ecstorage.dataframe as ec
from pyspark import SparkContext
from pyspark.mllib.linalg.distributed import *
from pyspark.sql import SparkSession
from ecstorage.mathematics.matrix_optimization import sparse
import numpy as np
import os
os.environ["PYSPARK_PYTHON"]="/Users/caiwei/opt/anaconda3/bin/python"
os.environ["PYSPARK_DRIVER_PYTHON"]="/Users/caiwei/opt/anaconda3/bin/python"

from pyspark.sql import SQLContext
m = 3                       #生成校验块个数
generator_matrix = 'vander' #生成矩阵选择范德蒙德矩阵

sc = SparkContext()
sqlContext = SQLContext(sc)

dicts = [
        {'col1':'a', 'col2':1},
        {'col1':'b', 'col2':2},
        {'col1':'b', 'col2':3},
        {'col1':'b', 'col2':4},
        {'col1':'b', 'col2':5},
         ]
df = sqlContext.createDataFrame(dicts)
data = df.select('col2')
# data.show()

check_block = ec.reedsolomon(sc,data,m)
check_block.show()


# 测试
dicts = [
        {'col1':'a', 'col2':None},
        {'col1':'b', 'col2':None},
        {'col1':'b', 'col2':3},
        {'col1':'b', 'col2':4},
        {'col1':'b', 'col2':5},
         ]
# # data[2] = None
# check_block = check_block.collect()
# check_block[0] = None
# check_block = sc.parallelize(check_block)
data = sqlContext.createDataFrame(dicts)
data = data.select('col2')
data.show()
# 恢复数据
recover_data = ec.verify(sc,data,check_block,generator_matrix)  
recover_data.show()
```

