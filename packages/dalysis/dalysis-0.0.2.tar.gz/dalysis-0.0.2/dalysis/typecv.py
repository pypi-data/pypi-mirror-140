import numpy
from datetime import datetime


def toDate(input,mod):
    if(isinstance(input,str)):
        return datetime.strptime(input, mod).date()
    elif( isinstance(input,list) ):
        res = input.copy()
        for i in range(0,len(res)):
            res[i] = datetime.strptime(res[i], mod).date()
        return res
    elif( isinstance(input,numpy.ndarray) ):
        res = input.copy()
        for i in range(0,len(res)):
            res[i] = datetime.strptime(res[i], mod).date()
        return res