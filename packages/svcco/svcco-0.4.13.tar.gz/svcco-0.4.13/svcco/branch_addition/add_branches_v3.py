import numpy as np
import os #remove before final
import time #not neccessary?
from .check import *
from .close import *
from .local_func_v6 import *
from ..collision.sphere_proximity import *
from ..collision.collision import *
from .add_bifurcation import *
from .sample_triad import *
from .triangle import * #might not need
from .basis import *
from scipy import interpolate
from scipy.spatial import KDTree
import matplotlib.pyplot as plt #remove before final
from .get_point import *
from mpl_toolkits.mplot3d import proj3d #remove before final
from .geodesic import extract_surface,geodesic
from ..implicit.visualize.visualize import show_mesh
from .finite_difference import finite_difference
from scipy.sparse.csgraph import shortest_path

def add_branch(tree,low,high,threshold_exponent=1.5,threshold_adjuster=0.75,
               all_max_attempts=40,max_attemps=10,sampling=20,max_skip=8,
               flow_ratio=8):
    number_edges       = tree.parameters['edge_num']
    threshold_distance = ((tree.boundary.volume)**(1/3)/
                         (number_edges**threshold_exponent))
    mu                 = tree.parameters['mu']
    lam                = tree.parameters['lambda']
    gamma              = tree.parameters['gamma']
    nu                 = tree.parameters['nu']
    Qterm              = tree.parameters['Qterm']
    Pperm              = tree.parameters['Pperm']
    Pterm              = tree.parameters['Pterm']
    new_branch_found   = False
    if tree.homogeneous:
        while not new_branch_found:
            total_attempts = 0
            attempt        = 0
            while total_attempts < all_max_attempts:
                point,_ = tree.boundary.pick(homogeneous=True)
                vessel, line_distances = close_exact(tree.data,point)
                line_distances_below_threshold = sum(line_distances < threshold_distance)
                minimum_line_distance = min(line_distances)
                if (line_distances_below_threshold == 0 and
                    minimum_line_distance > 4*tree.data[vessel[0],21]):
                    escape = False
                    for i in range(max_skip):
                        if tree.data[vessel[i],22] < flow_ratio*Qterm:
                            vessel = vessel[i]
                            escape = True
                            break
                    if escape:
                        break
                else:
                    if attempt < 10:
                        attempt += 1
                        total_attempts += 1
                    else:
                        #print('adjusting threshold')
                        threshold_distance *= threshold_adjuster
                        attempt = 0
            proximal = tree.data[vessel,0:3]
            distal   = tree.data[vessel,3:6]
            terminal = point
            points   = get_local_points(tree.data,vessel,terminal,sampling,tree.clamped_root)
            points   = relative_length_constraint(points,proximal,distal,terminal,0.25)
            if not tree.convex:
                points = boundary_constraint(points,tree.boundary,2)
            if len(points) == 0:
                continue
            points = angle_constraint(points,terminal,distal,-0.4,True)
            if len(points) == 0:
                continue
            points = angle_constraint(points,terminal,distal,0.75,False)
            if len(points) == 0:
                continue
            points = angle_constraint(points,terminal,proximal,0,False)
            if len(points) == 0:
                continue
            points = angle_constraint(points,distal,proximal,0,False)
            if len(points) == 0:
                continue
            if tree.data[vessel,17] >= 0:
                p_vessel = int(tree.data[vessel,17])
                vector_1 = -tree.data[p_vessel,12:15]
                vector_2 = (points - proximal)/np.linalg.norm(points - proximal,axis=1).reshape(-1,1)
                angle = np.array([np.dot(vector_1,vector_2[i]) for i in range(len(vector_2))])
                points = points[angle<0]
                if len(points) == 0:
                    continue
            results = fast_local_function(tree.data,points,terminal,
                                          vessel,gamma,nu,Qterm,Pperm,Pterm)
            volume  = np.pi*(results[0]**lam)*(results[1]**mu)
            idx     = np.argmin(volume)
            bif     = results[5][idx]
            no_collision = collision_free(tree.data,results,idx,terminal,
                                          vessel,tree.radius_buffer)
            if no_collision:
                new_branch_found = True
                data,sub_division_map,sub_division_index = add_bifurcation(tree,vessel,terminal,
                                                                           results,idx)
                return vessel,data,sub_division_map,sub_division_index
            else:
                continue
    else:
        reduced_data  = tree.data[tree.data[:,-1]>-1]
        segment_data  = tree.data[tree.data[:,-1]==-1]
        vessel        = np.random.choice(list(range(reduced_data.shape[0])))
        vessel_path   = segment_data[segment_data[:,29].astype(int)==vessel]
        other_vessels = segment_data[segment_data[:,29].astype(int)!=vessel]
        if reduced_data.shape[0] > 1:
            other_KDTree = KDTree((other_vessels[:,0:3]+other_vessels[:,3:6])/2)
        else:
            other_KDTree = None
        mesh,pa,cp,cd = tree.boundary.mesh(vessel_path[1:,0:3],threshold_distance,threshold_distance//fraction,dive=0,others=other_KDTree)
        D,PR = shortest_path(graph,directed=False,method="D",return_predecessors=True)
        bif_idx = set(list(range(mesh.shape[0])))
