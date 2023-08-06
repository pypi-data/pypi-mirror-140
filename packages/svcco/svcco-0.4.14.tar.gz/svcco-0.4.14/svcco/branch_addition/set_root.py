import numpy as np
from .basis import *
from .calculate_length import *
from .update import *
from .calculate_radii import *

def set_root(data, boundary, Qterm, gamma, nu,
             Pperm, Pterm, fraction,
             ishomogeneous,isconvex,isdirected,
             start,direction,limit_high,limit_low,
             low=-1,high=0):
    """
    Explaination of code
    """
    p0,layer = boundary.pick()
    distance = boundary.volume**(1/3)
    steps = distance//fraction
    if not ishomogeneous:
        path,lengths,layers = boundary.path(p0,distance,steps,dive=0)
        p1 = path[-1]
        path = np.array(path)
        data = np.zeros((len(path),data.shape[1]))
    elif start is None and direction is None:
        p1,_ = boundary.pick(homogeneous=True)
        lengths = [np.linalg.norm(p1-p0)]
    else:
        p0 = start
        if limit_high is not None and limit_low is not None:
            distance = limit_high - limit_low
            required_length = limit_low
        elif limit_high is not None and limit_low is None:
            distance = length_high
            required_length = 0
        p1_tmp = start + direction*required_length + direction*distance*np.random.random(1)
        while not boundary.within(p1_tmp[0],p1_tmp[1],p1_tmp[2],2):
            p1_tmp = start + direction*distance*np.random.random(1)
        p1 = p1_tmp
        lengths = [np.linalg.norm(p1-p0)]
    data[0, 0:3] = p0
    data[0, 3:6] = p1
    basis(data,0)
    data[0, 15] = -1
    data[0, 16] = -1
    data[0, 17] = -1
    data[0, 18] = 0
    data[0, 19] = 1
    data[0, 20] = np.sum(lengths)
    data[0, 22] = Qterm
    data[0, 26] = 0
    data[0, 28] = 1.0
    data[0, 29] = -1
    data[0, -1] = 0
    sub_division_map = [-1]
    sub_division_index = [0]
    update(data, gamma, nu)
    radii(data,Pperm,Pterm)
    if not ishomogeneous:
        for i in range(1,len(path)):
            if i == 1:
                data[i,0:3] = p0
                data[i,3:6] = path[i]
            #elif i == data.shape[0]:
            #    data[i,0:3] = path[-1]
            #    data[i,3:6] = p1
            else:
                data[i,0:3] = path[i-1]
                data[i,3:6] = path[i]
            basis(data,i)
            data[i,15] = -1
            data[i,16] = -1
            data[i,17] = -1
            data[i,18] = -1
            data[i,19] = -1
            data[i,20] = lengths[i]
            data[i,21] = data[0,21]
            data[i,22] = -1
            data[i,23] = -1
            data[i,24] = -1
            data[i,25] = -1
            data[i,26] = -1
            data[i,27] = -1
            data[i,28] = -1
            data[i,29] = 0
            data[i,-1] = -1
    return data,sub_division_map,sub_division_index
