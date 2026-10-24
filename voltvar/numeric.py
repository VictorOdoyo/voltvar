import math
def finite(value,name,minimum=None,maximum=None):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):raise ValueError(name+' must be finite numeric data')
    if minimum is not None and value<minimum or maximum is not None and value>maximum:raise ValueError(name+' is outside its permitted range')
    return float(value)
def integer(value,name,minimum,maximum):
    if isinstance(value,bool) or not isinstance(value,int) or not minimum<=value<=maximum:raise ValueError(name+' must be an integer in range')
    return value
