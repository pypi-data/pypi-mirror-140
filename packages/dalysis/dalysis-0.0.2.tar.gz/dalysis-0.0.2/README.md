# dalysis: for data analysis

I often need to deal with Excel and CSV table files in the process of numerical calculation and data analysis. And this is a package I wrote for the convenience of my own calculation.

**If you find that there are some problems in this package, or there are functions and codes that need to be improved, please contact me or help me complete these. Thank you very much.**

## Something About the package

the tree of this package

```bash
dalysis
│  table.py
│  typecv.py
│  __init__.py
```

### table.py

This module have functions *table.open_csv* and *table.open_excel* to  handles excel and csv and return a object whose type is <class 'table.Table'>

### typecv.py

This module have functions for type conversation.



A demo code:

```python
''' test data.csv:
date,value1,value2
2020/1/11,1,6
2020/1/12,3,3
2020/1/13,2,1
2020/1/14,7,8
2020/1/15,3,3
2020/1/16,1,1
2020/1/17,6,66
2020/1/18,8,33
2020/1/19,4,65
2020/1/20,9,32
2020/1/21,22,4
2020/1/22,45,33
2020/1/23,2,5
2020/1/24,7,3
2020/1/25,8,7
2020/1/26,0,4
2020/1/27,4,8
'''
from dalysis import table
from dalysis import typecv
import matplotlib.pyplot as plt

tb = table.open_csv( "test data.csv","r" )
tb.output()
plt.plot( typecv.toDate(tb.head('date'),"%y/%m/%d"),tb.head('value1') )

```

