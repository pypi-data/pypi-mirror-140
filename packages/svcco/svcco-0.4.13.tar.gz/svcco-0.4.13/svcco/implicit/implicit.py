from __future__ import print_function
import numba as nb
import vtk
from vtk.util import numpy_support
from scipy import optimize
from .visualize.visualize import *
from .sampling import *
from concurrent.futures import ProcessPoolExecutor as PPE
from concurrent.futures import as_completed
from functools import partial
from multiprocessing import Pool, RLock, freeze_support
from threading import RLock as TRLock
from .derivative import *
from tqdm.auto import tqdm, trange
from functools import partial
from .solver.solver import solver
from ..branch_addition.basis import tangent_basis
from pickle import dumps,loads
from scipy.spatial import cKDTree

import imp
import sys

from .core.m_matrix import M
from .core.n_matrix import N
from .core.a_matrix import A
from .core.h_matrix import H
from .load import load3d
from .visualize.visualize import show_mesh

class patch:
    def __init__(self,points,normals):
        self.ndim = points.shape[0]
        self.ddim = points.shape[1]
        self.points = points
        self.normals = normals
        self.A_inv,self.K00,self.K01,self.K11 = A(points)
        self.H_0 = H(self.K00,self.K01,self.K11,0)

    def solve(self,local_method='L-BFGS-B',regularize=False,
              local_verbosity=False,variational=False,
              solver_method='Bounded',solver_verbosity=False):
        if regularize:
            s = solver(self.points,self.normals)
            a,b = s.solve(local_verbosity=local_verbosity,local_method=local_method,
                          variational=variational,solver_method=solver_method,
                          solver_verbosity=solver_verbosity)
            self.a = a
            self.b = b
        else:
            g = np.zeros(self.ndim*3)
            M_inv = self.A_inv[:self.ndim*4,:self.ndim*4]
            N_inv = self.A_inv[:self.ndim*4,self.ndim*4:]
            for i in range(self.ndim):
                g[i] = self.normals[i,0]
                g[i+self.ndim] = self.normals[i,1]
                g[i+2*self.ndim] = self.normals[i,2]
            self.g = g
            s = np.zeros(self.ndim)
            l_side = np.zeros(M_inv.shape[1])
            l_side[:len(s)] = s
            l_side[len(s):(len(s)+len(g))] = g
            a = np.matmul(M_inv,l_side)
            b = np.matmul(N_inv.T,l_side)
            self.a = a
            self.b = b

class surface:
    def __init__(self):
        pass
    def load(self,filename):
        points,normals = load3d(filename)
        self.set_data(points,normals=normals)
    def set_data(self,points,normals=None,workers=1,local_min=10,local_max=20,l=0.5,PCA_samplesize=25):
        self.points = points
        self.ddim = points.shape[1]
        self.dim_range = [0]*self.ddim*2
        for i in range(self.ddim):
        	self.dim_range[i*2]   = min(points[:,i])
        	self.dim_range[i*2+1] = max(points[:,i])
        self.local_min = local_min
        self.local_max = local_max
        self.l = l
        self.workers = workers
        if np.any(normals) is None:
            point_cloud_vtk_array  = numpy_support.numpy_to_vtk(points,deep=True)
            point_cloud_vtk_points = vtk.vtkPoints()
            point_cloud_vtk_points.SetData(point_cloud_vtk_array)
            point_cloud_polydata   = vtk.vtkPolyData()
            point_cloud_polydata.SetPoints(point_cloud_vtk_points)
            PCA_normals            = vtk.vtkPCANormalEstimation()
            PCA_normals.SetInputData(point_cloud_polydata)
            PCA_normals.SetSampleSize(PCA_samplesize)
            PCA_normals.SetNormalOrientationToGraphTraversal()
            PCA_normals.Update()
            PCA_polydata = PCA_normals.GetOutput()
            PCA_vtk_pts  = PCA_polydata.GetPointData()
            vtk_normals  = PCA_vtk_pts.GetNormals()
            self.normals = numpy_support.vtk_to_numpy(vtk_normals)
        else:
            self.normals = normals

    @staticmethod
    def patch_constructor_progress(tuple_data, auto_position=False,
                                   write_safe=False, blocking=True,
                                   progress=True,regularize=False,
                                   local_verbosity=False,local_method='L-BFGS-B',
                                   variational=False,solver_method='Bounded',
                                   solver_verbosity=True):
        points = tuple_data[0]
        normals = tuple_data[1]
        chunk = tuple_data[2]
        patches = []
        total = len(points)
        text = "Processing Chunk {0}  : ".format(chunk)
        for i in trange(total, desc=text, leave=False, disable=not progress,
                        lock_args=None if blocking else (False,),
                        position=None if auto_position else chunk):
            p_tmp = patch(points[i],normals[i])
            p_tmp.solve(regularize=regularize,local_verbosity=local_verbosity,
                        local_method=local_method,variational=varitaional,
                        solver_method=solver_method,solver_verbosity=solver_verbosity)
            patches.append(p_tmp)
        return patches

    @staticmethod
    def patch_constructor_no_progress(tuple_data, auto_position=False,
                                      write_safe=False, blocking=True,
                                      progress=True,regularize=False,
                                      local_verbosity=False,local_method='L-BFGS-B',
                                      variational=False,solver_method='Bounded',
                                      solver_verbosity=True):
        points = tuple_data[0]
        normals = tuple_data[1]
        chunk = tuple_data[2]
        patches = []
        total = len(points)
        for i in range(total):
            p_tmp = patch(points[i],normals[i])
            p_tmp.solve(regularize=regularize,local_verbosity=local_verbosity,
                        local_method=local_method,variational=variational,
                        solver_method=solver_method,solver_verbosity=solver_verbosity)
            patches.append(p_tmp)
        return patches

    def parallel_build(self,chunks,show_individual=False,PU=True):
        patches = []
        if show_individual and PU:
            freeze_support()
            tqdm.set_lock(RLock())
            executor = PPE(max_workers=len(chunks),initializer=tqdm.set_lock,initargs=(tqdm.get_lock(),))
            patch_function = partial(self.patch_constructor_no_progress,regularize=self.__regularize__,
                                     local_verbosity=self.__local_verbosity__,local_method=self.__local_method__,
                                     variational=self.__variational__,solver_method=self.__solver_method__,
                                     solver_verbosity=self.__solver_verbosity__)
            futures = {executor.submit(patch_function,chunk): chunk for chunk in chunks}
        elif self.workers == 1 and PU:
            patch_function = partial(self.patch_constructor_no_progress,regularize=self.__regularize__,
                                     local_verbosity=self.__local_verbosity__,local_method=self.__local_method__,
                                     variational=self.__variational__,solver_method=self.__solver_method__,
                                     solver_verbosity=self.__solver_verbosity__)
            futures = patch_function(chunks[0])
        elif PU:
            executor = PPE(max_workers=len(chunks))
            patch_function = partial(self.patch_constructor_no_progress,regularize=self.__regularize__,
                                     local_verbosity=self.__local_verbosity__,local_method=self.__local_method__,
                                     variational=self.__variational__,solver_method=self.__solver_method__,
                                     solver_verbosity=self.__solver_verbosity__)
            futures = {executor.submit(patch_function,chunk): chunk for chunk in chunks}
        else:
            global_patch = patch(self.points,self.normals)
            global_patch.solve(local_method=self.__local_method__,regularize=self.__regularize__,
                               local_verbosity=self.__local_verbosity__,variational=self.__variational__,
                               solver_method=self.__solver_method__,solver_verbosity=self.__solver_verbosity__)
        total_patches = []
        if show_individual and PU:
            for future in as_completed(futures):
                 total_patches.extend(future.result())
        elif self.workers == 1 and PU:
            total_patches = futures
        elif PU:
            for future in as_completed(futures):
                total_patches.extend(future.result())
        else:
            total_patches.append(global_patch)
        if self.workers != 1:
            executor.shutdown()
        return total_patches

    def solve(self,angle=0,PU=True,show_individual=False,regularize=False,
              local_verbosity=False,local_method='L-BFGS-B',variational=False,
              solver_method='Bounded',solver_verbosity=False,quiet=True):
        self.__regularize__ = regularize
        self.__local_verbosity__ = local_verbosity
        self.__local_method__ = local_method
        self.__variational__ = variational
        self.__solver_method__ = solver_method
        self.__solver_verbosity__= solver_verbosity
        if PU:
            patches,idxs,KDTree,centers = sampling(self.points,
                                           normals=self.normals,
                                           min_local_size=self.local_min,
                                           max_local_size=self.local_max,l=self.l,
                                           angle=angle,quiet=quiet)
            patches = []
            patch_centers = []
            patch_center_idx = []
            self.max_patch_size = 0
            chunksize = len(idxs)//self.workers
            number_of_chunks = len(idxs)//chunksize
            chunks = []
            for i in range(number_of_chunks):
                tmp_points = []
                tmp_normals = []
                if i < number_of_chunks-1:
                    if quiet:
                        for j in range(i*chunksize,i*chunksize+chunksize):
                            tmp_points.append(self.points[idxs[j]])
                            tmp_normals.append(self.normals[idxs[j]])
                            if len(idxs[j]) > self.max_patch_size:
                                self.max_patch_size = len(idxs[j])
                    else:
                        for j in tqdm(range(i*chunksize,i*chunksize+chunksize),desc='Building Chunk {}       '.format(i)):
                            tmp_points.append(self.points[idxs[j]])
                            tmp_normals.append(self.normals[idxs[j]])
                            if len(idxs[j]) > self.max_patch_size:
                                self.max_patch_size = len(idxs[j])
                    chunk_chunk = i
                    chunks.append([tmp_points,tmp_normals,chunk_chunk])
                else:
                    if i*chunksize >= len(idxs):
                        break
                    else:
                        if quiet:
                            for j in range(i*chunksize,len(idxs)):
                                tmp_points.append(self.points[idxs[j]])
                                tmp_normals.append(self.normals[idxs[j]])
                                if len(idxs[j]) > self.max_patch_size:
                                    self.max_patch_size = len(idxs[j])
                        else:
                            for j in tqdm(range(i*chunksize,len(idxs)),desc='Building Chunk {}       '.format(i)):
                                tmp_points.append(self.points[idxs[j]])
                                tmp_normals.append(self.normals[idxs[j]])
                                if len(idxs[j]) > self.max_patch_size:
                                    self.max_patch_size = len(idxs[j])
                        chunk_chunk = i
                        chunks.append([tmp_points,tmp_normals,chunk_chunk])
            _ = patch(chunks[0][0][0],chunks[0][1][0])
            self.patches = self.parallel_build(chunks,show_individual=show_individual)
        else:
            self.max_patch_size = self.points.shape[0]
            self.patches = self.parallel_build(None,show_individual=show_individual,PU=PU)

    def build(self,h=0,q=1,d_num=2):
        self.x_range = [min(self.points[:,0]),max(self.points[:,0])]
        self.y_range = [min(self.points[:,1]),max(self.points[:,1])]
        self.z_range = [min(self.points[:,2]),max(self.points[:,2])]
        solution_matrix = []
        a_coef          = []
        b_coef          = []
        b_sol           = []
        n_points        = []
        patch_points    = []
        patch_x         = []
        patch_y         = []
        patch_z         = []
        patch_points_m  = []
        for patch in self.patches:
            solution_matrix_tmp = np.empty((self.max_patch_size,len(patch.b)))
            b_sol_tmp = np.zeros((self.max_patch_size,len(patch.b)))
            points = np.empty((self.max_patch_size,len(patch.b)-1))
            patch_points_m.append(patch.points)
            solution_matrix_tmp.fill(np.nan)
            points.fill(np.nan)
            points[:patch.ndim,:] = patch.points
            a_coef.append(patch.a)
            b_coef.append(patch.b)
            n_points.append(patch.ndim)
            patch_points.append(points)
            patch_x.append(patch.points[0,0])
            patch_y.append(patch.points[0,1])
            patch_z.append(patch.points[0,2])
            solution_matrix_tmp[:patch.ndim,0] = patch.a[:patch.ndim]
            b_sol_tmp[0,:] = patch.b
            for point in range(patch.ndim):
                solution_matrix_tmp[point,1] = patch.a[patch.ndim+point]
                solution_matrix_tmp[point,2] = patch.a[patch.ndim*2+point]
                solution_matrix_tmp[point,3] = patch.a[patch.ndim*3+point]
            solution_matrix.append(solution_matrix_tmp)
            b_sol.append(b_sol_tmp)
        if len(self.patches) > 1:
            functions = []
            KDTree = spatial.KDTree(np.array([patch_x,patch_y,patch_z]).T)
            preassembled_functions,function_strings = construct(d_num)
            foo = imp.new_module("foo")
            sys.modules["foo"] = foo
            pickled_DD = []
            DD = []
            exec("import numpy as np",foo.__dict__)
            for fss in function_strings:
                exec(fss,foo.__dict__)
            function_names = list(filter(lambda item: '__' not in item,dir(foo)))
            for fn in function_names:
                if fn == 'np':
                    continue
                exec("pickled_DD.append(dumps(partial(foo.{},KDTree=KDTree,patch_points".format(fn)+\
                     "=np.array(patch_points),b_coef=np.array(b_sol),h=h,q=q,sol_mat=np"+\
                     ".array(solution_matrix),patch_1=np.array(patch_x),patch_2=np.arra"+\
                     "y(patch_y),patch_3=np.array(patch_z))))")
                exec("DD.append(partial(foo.{},KDTree=KDTree,patch_points".format(fn)+\
                     "=np.array(patch_points),b_coef=np.array(b_sol),h=h,q=q,sol_mat=np"+\
                     ".array(solution_matrix),patch_1=np.array(patch_x),patch_2=np.arra"+\
                     "y(patch_y),patch_3=np.array(patch_z)))")
            func_marching = partial(function_marching,patch_points=patch_points_m,
                                    a_coef=a_coef,b_coef=b_coef,h=h,q=q,
                                    patch_x=np.array(patch_x),patch_y=np.array(patch_y),
                                    patch_z=np.array(patch_z))
            #ls_d0 = partial(linesearch_d1,patch_points=np.array(patch_points),
            #                b_coef=np.array(b_sol),h=h,q=q,sol_mat=np.array(solution_matrix),
            #                patch_1=np.array(patch_x),patch_2=np.array(patch_y),
            #                patch_3=np.array(patch_z))
            #ls_d1 = partial(linesearch_d1,patch_points=np.array(patch_points),
            #                b_coef=np.array(b_sol),h=h,q=q,sol_mat=np.array(solution_matrix),
            #                patch_1=np.array(patch_x),patch_2=np.array(patch_y),
            #                patch_3=np.array(patch_z))
            #ls_d2 = partial(linesearch_d2,patch_points=np.array(patch_points),
            #                b_coef=np.array(b_sol),h=h,q=q,sol_mat=np.array(solution_matrix),
            #                patch_1=np.array(patch_x),patch_2=np.array(patch_y),
            #                patch_3=np.array(patch_z))
            self.function_marching = func_marching
            #self.linesearch_d0 = ls_d0
            #self.linesearch_d1 = ls_d1
            #self.linesearch_d2 = ls_d2
        else:
            functions = []
            preassembled_functions,function_strings = construct_global(d_num)
            foo = imp.new_module("foo")
            sys.modules["foo"] = foo
            pickled_DD = []
            DD = []
            exec("import numpy as np",foo.__dict__)
            for fss in function_strings:
                exec(fss,foo.__dict__)
            function_names = list(filter(lambda item: '__' not in item,dir(foo)))
            for fn in function_names:
                if fn == 'np':
                    continue
                exec("pickled_DD.append(dumps(partial(foo.{},patch_points=np.array(patch_points),b_coef=np.array(b_sol),sol_mat=np.array(solution_matrix))))".format(fn))
                exec("DD.append(partial(foo.{},patch_points=np.array(patch_points),b_coef=np.array(b_sol),sol_mat=np.array(solution_matrix)))".format(fn))
        self.pickled_DD = pickled_DD
        self.DD = DD
        self._get_properties_()
        """
        DD = []
        CDD = []
        for f in functions:
            if len(self.patches) > 1:
                DD.append(partial(f,KDTree=KDTree,patch_points=np.array(patch_points),
                                  b_coef=np.array(b_sol),h=h,q=q,sol_mat=np.array(solution_matrix),
                                  patch_1=np.array(patch_x),patch_2=np.array(patch_y),
                                  patch_3=np.array(patch_z)))
            else:
                tmp_DD = partial(foo,patch_points=np.array(patch_points),b_coef=np.array(b_sol),
                                 sol_mat=np.array(solution_matrix))
                CDD.append(dumps(tmp_DD))
                DD.append(tmp_DD)
        if len(self.patches) > 1:
            func = partial(function,KDTree=KDTree,patch_points=np.array(patch_points),
                           b_coef=np.array(b_coef),h=h,q=q,sol_mat=np.array(solution_matrix),
                           patch_x=np.array(patch_x),patch_y=np.array(patch_y),
                           patch_z=np.array(patch_z))
            func_marching = partial(function_marching,patch_points=patch_points_m,
                                    a_coef=a_coef,b_coef=b_coef,h=h,q=q,
                                    patch_x=np.array(patch_x),patch_y=np.array(patch_y),
                                    patch_z=np.array(patch_z))
            grad = partial(gradient,KDTree=KDTree,patch_points=np.array(patch_points),
                           b_coef=np.array(b_coef),h=h,q=q,sol_mat=np.array(solution_matrix),
                           patch_x=np.array(patch_x),patch_y=np.array(patch_y),
                           patch_z=np.array(patch_z))
            self.function = func
            self.function_marching = func_marching
            self.gradient = grad
        self.DD = DD
        self.CDD = CDD
        """
    def within(self,x,y,z,k):
        return self.DD[0]([x,y,z,k]) < 0

    def pick(self,**kwargs):
        homogeneous = kwargs.get('homogeneous',False)
        if homogeneous:
            point = None
            while point is None:
                x = np.random.uniform(self.x_range[0],self.x_range[1])
                y = np.random.uniform(self.y_range[0],self.y_range[1])
                z = np.random.uniform(self.z_range[0],self.z_range[1])
                if self.within(x,y,z,2):
                    point = np.array([x,y,z])
                    break
            return point,None
        x = np.random.uniform(self.x_range[0],self.x_range[1])
        y = np.random.uniform(self.y_range[0],self.y_range[1])
        z = np.random.uniform(self.z_range[0],self.z_range[1])
        k     = kwargs.get('k',len(self.patches))
        layer = kwargs.get('layer',0)
        x0    = kwargs.get('x0',np.array([x,y,z]))
        f     = lambda x: (self.DD[0]([x[0],x[1],x[2],k])-layer)**2
        df    = lambda x: 2*(self.DD[0]([x[0],x[1],x[2],k])-layer)*self.DD[1]([x[0],x[1],x[2],k])
        #ddf   = lambda x,y,z: 2*np.dot(self.DD[1]([x,y,z,k],self.DD[1]([x,y,z,k]))+2*self.DD[2]([x,y,z,k])*(self.DD[0]([x,y,z,k])-layer)
        res   = optimize.minimize(f,x0,method='L-BFGS-B')
        return res.x,res.fun

    def path(self,start,distance,steps,dive=0.01,theta_steps=40):
        start_layer = self.DD[0]([start[0],start[1],start[2],len(self.patches)])
        theta = np.linspace(0,2*np.pi,theta_steps)
        path = [start]
        path_d = [0]
        path_layer = [start_layer]
        point = start
        while np.sum(path_d) < distance:
            normal = self.DD[1]([point[0],point[1],point[2],max(round(len(self.patches)),2)])
            t1,t2,unit_normal = tangent_basis(normal,point)
            next_steps = path[-1] + (distance/steps)*(t1*np.cos(theta).reshape(-1,1)+t2*np.sin(theta).reshape(-1,1)) #-(dive/steps)*(unit_normal)
            distances  = np.linalg.norm(next_steps - path[-1],axis=1)
            distances1 = np.linalg.norm(next_steps - path[0],axis=1)+np.linalg.norm(next_steps - path[-1],axis=1)
            next_step  = next_steps[np.argmax(distances1),:]
            next_step,next_layer = self.pick(layer=path_layer[-1]-(dive/steps),x0=next_step)
            path_layer.append(next_layer)
            path_d.append(distances[np.argmax(distances)])
            path.append(next_step)
            point = next_step
        return path,path_d,path_layer

    def mesh(self,path,distance,steps,dive=0.01,theta_steps=40,others=None):
        center = round(len(path)*0.5)
        start  = path[center]
        start_layer = self.DD[0]([start[0],start[1],start[2],len(self.patches)])
        ###################
        ###################
        theta = np.linspace(0,2*np.pi,theta_steps)
        center_path = [start]
        path_d = []
        path_layer = [start_layer]
        point = start
        direction = (path[center+1] - path[center-1])/np.linalg.norm(path[center+1] - path[center-1])
        while np.sum(path_d) < distance:
            normal = self.DD[1]([point[0],point[1],point[2],max(round(len(self.patches)*0.1),2)])
            t1,t2,unit_normal = tangent_basis(normal,point)
            next_steps = center_path[-1] + (distance/steps)*(t1*np.cos(theta).reshape(-1,1)+
                                                             t2*np.sin(theta).reshape(-1,1)) #-(dive/steps)*(unit_normal)
            distances  = np.linalg.norm(next_steps - center_path[-1],axis=1)
            if len(center_path) == 1:
                distances1 = np.linalg.norm(next_steps - center_path[0],axis=1)+np.linalg.norm(next_steps - path[center+1],axis=1)+np.linalg.norm(next_steps - path[center-1],axis=1)
            else:
                #distances1 = np.linalg.norm(next_steps - center_path[0],axis=1)+np.linalg.norm(next_steps - center_path[-1],axis=1)+\
                if others is None:
                    distances1 = (1 - np.sum(path_d)/distance)*np.linalg.norm(next_steps - center_path[0],axis=1)+np.sum(path_d)/distance*np.linalg.norm(next_steps - center_path[-1],axis=1)
                else:
                    other_dist,_ = others.query(next_steps,k=1)
                    distances1 = (1 - np.sum(path_d)/distance)*np.linalg.norm(next_steps - center_path[0],axis=1)+np.sum(path_d)/distance*np.linalg.norm(next_steps - center_path[-1],axis=1)+\
                                 (other_dist)
            next_step  = next_steps[np.argmax(distances1),:]
            next_step,next_layer = self.pick(layer=path_layer[-1]-(dive/steps),x0=next_step)
            path_layer.append(next_layer)
            path_d.append(distances[np.argmax(distances)])
            center_path.append(next_step)
            point = next_step
        past_up = []
        past_down = []
        mesh = []
        #mesh.extend(center_path)
        #mesh.extend(path)
        up_past = []
        down_past = []
        past_point_up = []
        past_point_down = []
        past_line = center_path
        #Upper triangle Mesh
        #print('Max Center Path: {}'.format(len(path[center+1:])))
        for i in range(len(path[center+1:-1])):
            ii = i + center +1
            point = path[ii]
            line = [point]
            percent = round(min((1-i/len(path[center+1:])),1)*len(center_path))
            #print(percent)
            for j in range(1,percent):
                normal = self.DD[1]([point[0],point[1],point[2],max(round(len(self.patches)*0.1),2)])
                m1 = (past_line[j] - past_line[j-1])/np.linalg.norm(past_line[j] - past_line[j-1])
                m2 = (point - past_line[j-1])/np.linalg.norm(line[-1] - past_line[j-1])
                predicted = past_line[j-1] + m1*(distance/steps)+m2*(distance/steps)
                t1,t2,unit_normal = tangent_basis(normal,point)
                next_steps = point + (distance/steps)*(t1*np.cos(theta).reshape(-1,1)+t2*np.sin(theta).reshape(-1,1))
                distances = np.linalg.norm(next_steps - predicted,axis=1)
                line.append(next_steps[np.argmin(distances),:])
                point = line[-1]
            past_line = line
            mesh.extend(line)
            #show_mesh(np.array(mesh),np.array(path),np.array(center_path))
        past_line = center_path
        #Lower Triangle Mesh
        for i in range(len(path[1:center-1])):
            ii = center -1-i
            point = path[ii]
            line = [point]
            percent = round(min((1-i/len(path[:center-1])),1)*len(center_path))
            for j in range(1,percent):
                normal = self.DD[1]([point[0],point[1],point[2],max(round(len(self.patches)*0.1),2)])
                m1 = (past_line[j] - past_line[j-1])/np.linalg.norm(past_line[j] - past_line[j-1])
                m2 = (point - past_line[j-1])/np.linalg.norm(line[-1] - past_line[j-1])
                predicted = past_line[j-1] + m1*(distance/steps)+m2*(distance/steps)
                t1,t2,unit_normal = tangent_basis(normal,point)
                next_steps = point + (distance/steps)*(t1*np.cos(theta).reshape(-1,1)+t2*np.sin(theta).reshape(-1,1))
                distances = np.linalg.norm(next_steps - predicted,axis=1)
                line.append(next_steps[np.argmin(distances),:])
                point = line[-1]
            past_line = line
            mesh.extend(line)
        #proximal = path[0]
        #distal = path[-1]
        #terminal = center_path[-1]
        #mesh.insert(0,terminal)
        #mesh.insert(0,distal)
        #mesh.insert(0,proximal)
        mesh = np.array(mesh)
        mesh_tree = cKDTree(mesh)
        graph = mesh_tree.sparse_distance_matrix(mesh_tree,((distance/steps)**2+(dive/steps)**2)*(1/2))
        return mesh,path,center_path,path_d,graph

    def _get_properties_(self,**kwargs):
        resolution = kwargs.get('resolution',20)
        k          = kwargs.get('k',2)
        level      = kwargs.get('level',0)
        visualize  = kwargs.get('visualize',False)
        self.polydata   = marching_cubes(self,resolution)
        volume,surface_area = properties(self.polydata)
        self.volume= volume
        self.surface_area = surface_area

def marching_cubes(surface_object,resolution=20,k=2,level=0,visualize=False):
    """
    Takes an interpolated volume and performs
    a descritization on a selected hyperplane.
    """
    surface_algorithm = vtk.vtkMarchingCubes()
    image_data        = vtk.vtkImageData()
    X,Y,Z = np.mgrid[surface_object.x_range[0]-1:surface_object.x_range[1]+1:resolution*1j,
                     surface_object.y_range[0]-1:surface_object.y_range[1]+1:resolution*1j,
                     surface_object.z_range[0]-1:surface_object.z_range[1]+1:resolution*1j]
    SHAPE = (resolution,resolution,resolution)
    SPACING = ((surface_object.x_range[1]-surface_object.x_range[0]+2)/(resolution-1),
               (surface_object.y_range[1]-surface_object.y_range[0]+2)/(resolution-1),
               (surface_object.z_range[1]-surface_object.z_range[0]+2)/(resolution-1))
    Xf = X.flatten()
    Yf = Y.flatten()
    Zf = Z.flatten()
    Kf = np.ones(Xf.shape,dtype=int)*k
    #Sample Implicit Function
    print('Sampling Implicit Volume...')
    Vf = []
    for i in zip(Xf,Yf,Zf,Kf):
        Vf.append(surface_object.DD[0](i))
    print('Converting to VTK Image Data...')
    data_vtk = numpy_support.numpy_to_vtk(Vf,deep=1,array_type=vtk.VTK_FLOAT)
    image_data.SetDimensions(SHAPE)
    image_data.SetSpacing(SPACING)
    image_data.GetPointData().SetScalars(data_vtk)
    print('Marching...')
    surface_algorithm.SetInputData(image_data)
    surface_algorithm.ComputeNormalsOn()
    surface_algorithm.SetValue(0,level)

    if visualize:
        colors = vtk.vtkNamedColors()

        renderer = vtk.vtkRenderer()
        renderer.SetBackground(colors.GetColor3d('White'))

        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        render_window.SetWindowName('Marching Cubes')

        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(surface_algorithm.GetOutputPort())
        mapper.ScalarVisibilityOff()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        actor.GetProperty().SetColor(colors.GetColor3d('MistyRose'))

        renderer.AddActor(actor)

        render_window.Render()
        interactor.Start()
    else:
        surface_algorithm.Update()
    return surface_algorithm.GetOutput()

def properties(polydata_object):
    MASS = vtk.vtkMassProperties()
    MASS.SetInputData(polydata_object)
    MASS.Update()
    return MASS.GetVolume(),MASS.GetSurfaceArea()
