from scipy.interpolate import splprep, splev
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from mpl_toolkits.mplot3d import Axes3D, proj3d, art3d
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from ..branch_addition.basis import tangent_basis

from mpl_toolkits.mplot3d import art3d

def rotation_matrix(d):
    """
    Calculates a rotation matrix given a vector d. The direction of d
    corresponds to the rotation axis. The length of d corresponds to
    the sin of the angle of rotation.

    Variant of: http://mail.scipy.org/pipermail/numpy-discussion/2009-March/040806.html
    """
    sin_angle = np.linalg.norm(d)

    if sin_angle == 0:
        return np.identity(3)

    d /= sin_angle

    eye = np.eye(3)
    ddt = np.outer(d, d)
    skew = np.array([[    0,  d[2],  -d[1]],
                  [-d[2],     0,  d[0]],
                  [d[1], -d[0],    0]], dtype=np.float64)

    M = ddt + np.sqrt(1 - sin_angle**2) * (eye - ddt) + sin_angle * skew
    return M

def pathpatch_2d_to_3d(pathpatch, z = 0, normal = 'z'):
    """
    Transforms a 2D Patch to a 3D patch using the given normal vector.

    The patch is projected into they XY plane, rotated about the origin
    and finally translated by z.
    """
    if type(normal) is str: #Translate strings to normal vectors
        index = "xyz".index(normal)
        normal = np.roll((1.0,0,0), index)

    normal /= np.linalg.norm(normal) #Make sure the vector is normalised

    path = pathpatch.get_path() #Get the path and the associated transform
    trans = pathpatch.get_patch_transform()

    path = trans.transform_path(path) #Apply the transform

    pathpatch.__class__ = art3d.PathPatch3D #Change the class
    pathpatch._code3d = path.codes #Copy the codes
    pathpatch._facecolor3d = pathpatch.get_facecolor #Get the face color

    verts = path.vertices #Get the vertices in 2D

    d = np.cross(normal, (0, 0, 1)) #Obtain the rotation vector
    M = rotation_matrix(d) #Get the rotation matrix

    pathpatch._segment3d = np.array([np.dot(M, (x, y, 0)) + (0, 0, z) for x, y in verts])

def pathpatch_translate(pathpatch, delta):
    """
    Translates the 3D pathpatch by the amount delta.
    """
    pathpatch._segment3d += delta

def get_longest_path(data,seed_edge):
    dig = True
    temp_edges = [seed_edge]
    while dig:
        keep_digging = []
        for edge in temp_edges:
            if data[edge,15] > -1:
                temp_edges.extend([int(data[edge,15]), int(data[edge,16])])
                temp_edges.remove(edge)
                keep_digging.append(True)
            else:
                keep_digging.append(False)
        dig = any(keep_digging)
    if len(temp_edges) == 1:
        return temp_edges
    edge_depths = []
    for edge in temp_edges:
        edge_depths.append(data[edge,26])
    max_depth = max(edge_depths)
    max_edge_depths = [i for i,j in enumerate(edge_depths) if j == max_depth]
    paths = [[temp_edges[i]] for i in max_edge_depths]
    path_lengths = [data[i[0],20] for i in paths]
    retrace = True
    while retrace:
        for i, path in enumerate(paths):
            path.insert(0,int(data[path[0],17]))
            path_lengths[i] += data[path[0],20]
        if paths[0][0] == seed_edge:
            retrace = False
    return paths[path_lengths.index(max(path_lengths))]

def get_alternate_path(data,seed_edge,reference=None):
    if reference is None:
        reference = get_longest_path(data,seed_edge)
    else:
        pass
    seed_edge_idx = reference.index(seed_edge)
    if seed_edge_idx == len(reference)-1:
        print('Seed edge is terminal and no alternative is '+
              'possible. \n Computation finished.')
        return None
    else:
        children = [int(data[seed_edge,15]),int(data[seed_edge,16])]
        if children[0] not in reference:
            alternate_path = get_longest_path(data,children[0])
        else:
            alternate_path = get_longest_path(data,children[1])
    alternate_path.insert(0,seed_edge)
    return alternate_path

def get_branches(data):
    branches = []
    seed_edge = 0
    path = get_longest_path(data,seed_edge)
    branches.append(path)
    upcoming_evaluations = []
    upcoming_evaluations.extend(path[:-1])
    counter = [len(path[:-1])]
    idx = 0
    while len(upcoming_evaluations) > 0:
        path = get_alternate_path(data,upcoming_evaluations.pop(-1),reference=branches[idx])
        counter[idx] -= 1
        if counter[idx] == 0:
            counter[idx] = None
            for i in reversed(range(len(counter))):
                if counter[i] is not None:
                    idx = i
                    break
        branches.append(path)
        if len(path) > 2:
            upcoming_evaluations.extend(path[1:-1])
            counter.append(len(path[1:-1]))
            idx = len(counter) - 1
        else:
            counter.append(None)
    return branches

def get_points(data,branches):
    path_points = []
    primed = False
    for path in branches:
        branch_points = []
        for edge in reversed(path):
            if edge == path[0] and primed:
                branch_points.insert(0,data[edge,3:6].tolist())
            elif edge == path[0] and edge == 0 and not primed:
                branch_points.insert(0,data[edge,3:6].tolist())
                mid_point = (data[edge,0:3] + data[edge,3:6])/2
                branch_points.insert(0,mid_point.tolist())
                branch_points.insert(0,data[edge,0:3].tolist())
                primed = True
            elif len(branch_points) == 0:
                branch_points.insert(0,data[edge,3:6].tolist())
                mid_point = (data[edge,0:3] + data[edge,3:6])/2
                branch_points.insert(0,mid_point.tolist())
            else:
                branch_points.insert(0,data[edge,3:6].tolist())
                mid_point = (data[edge,0:3] + data[edge,3:6])/2
                branch_points.insert(0,mid_point.tolist())
        path_points.append(branch_points)
    return path_points

def get_radii(data,branches):
    path_radii = []
    primed = False
    for path in branches:
        branch_radii = []
        for edge in reversed(path):
            if edge == path[0] and primed:
                branch_radii.insert(0,data[path[1],21])
            elif edge == path[0] and edge == 0 and not primed:
                branch_radii.insert(0,data[edge,21])
                branch_radii.insert(0,data[edge,21])
                branch_radii.insert(0,data[edge,21])
                primed = True
            elif len(branch_radii) == 0:
                branch_radii.insert(0,data[edge,21])
                branch_radii.insert(0,data[edge,21])
            else:
                branch_radii.insert(0,data[edge,21])
                branch_radii.insert(0,data[edge,21])
        path_radii.append(branch_radii)
    return path_radii

def get_normals(data,branches):
    path_normals = []
    primed = False
    for path in branches:
        branch_normals = []
        for edge in reversed(path):
            if edge == path[0] and primed:
                branch_normals.insert(0,data[path[1],12:15].tolist())
            elif edge == path[0] and edge == 0 and not primed:
                vector_1 = data[edge,12:15]
                mid_vector = (vector_1+vector_2)/2
                branch_normals.insert(0,mid_vector.tolist())
                branch_normals.insert(0,data[edge,12:15].tolist())
                branch_normals.insert(0,data[edge,12:15].tolist())
                primed = True
            elif len(branch_normals) == 0:
                branch_normals.insert(0,data[edge,12:15].tolist())
                branch_normals.insert(0,data[edge,12:15].tolist())
                vector_2 = data[edge,12:15]
            else:
                vector_1 = data[edge,12:15]
                mid_vector = (vector_1+vector_2)/2
                branch_normals.insert(0,mid_vector.tolist())
                branch_normals.insert(0,data[edge,12:15].tolist())
                vector_2 = data[edge,12:15]
        path_normals.append(branch_normals)
    return path_normals

def plot_sv_data(data):
    branches = get_branches(data)
    points   = get_points(data,branches)
    radii    = get_radii(data,branches)
    normals  = get_normals(data,branches)
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    for path in points:
        tmp = np.array(path)
        ax.plot3D(tmp[:,0],tmp[:,1],tmp[:,2])
        ax.scatter3D(tmp[:,0],tmp[:,1],tmp[:,2])
    plt.show()

def get_interpolated_sv_data(data):
    branches = get_branches(data)
    points   = get_points(data,branches)
    radii    = get_radii(data,branches)
    normals  = get_normals(data,branches)
    path_frames = []
    for idx in range(len(branches)):
        frames = []
        for jdx in range(len(points[idx])):
            frame = []
            frame.extend(points[idx][jdx])
            frame.append(radii[idx][jdx])
            frame.extend(normals[idx][jdx])
            frames.append(frame)
        path_frames.append(frames)
    interps = []
    for idx in range(len(branches)):
        if len(path_frames[idx]) == 2:
            interps.append(splprep(np.array(path_frames[idx]).T,k=1,s=0))
        elif len(path_frames[idx]) == 3:
            interps.append(splprep(np.array(path_frames[idx]).T,k=2,s=0))
        else:
            interps.append(splprep(np.array(path_frames[idx]).T,s=0))
    return interps,path_frames,branches

def get_sv_data(network):
    if isinstance(network,tree):
        data     = network.data
        branches = get_branches(data)
        points   = get_points(data,branches)
        radii    = get_radii(data,branches)
        normals  = get_normals(data,branches)
    elif isinstance(network,forest):
        for idx, grafts in enumerate(network.grafts):
            data        = []
            branches    = []
            connections = []
            for jdx, graft in enumerate(grafts):
                data.append(graft.data)
                branches.append(get_branches(graft.data))
                connections.append(network.connections[idx][jdx])

def plot_interp_vessels(interps,normals=True):
    n = np.linspace(0,1,200)
    fig = plt.figure()
    ax1  = fig.add_subplot(111,projection='3d')
    #ax2  = fig.add_subplot(232,projection='3d')
    #ax3  = fig.add_subplot(233,projection='3d')
    #ax4  = fig.add_subplot(234,projection='3d')
    #ax5  = fig.add_subplot(235,projection='3d')
    #ax6  = fig.add_subplot(236,projection='3d')
    for idx,b in enumerate(interps):
        if idx > 0:
            break
        x,y,z,r,nx,ny,nz = splev(n,b[0])
        nx,ny,nz,dr,dnx,dny,dnz = splev(n,b[0],der=1)
        nxx,nyy,nzz,_,_,_,_ = splev(n,b[0],der=2)
        #nxxx,nyyy,nzzz,_,_,_,_ = splev(n,b[0],der=3)
        ax1.plot3D(x,y,z,c='b')
        ax1.scatter3D(x[0],y[0],z[0],c='black')
        ax1.scatter3D(x[-1],y[-1],z[-1],c='black')
        #ax2.plot3D(x,y,z,c='b')
        #ax3.plot3D(x,y,z,c='b')
        idx_x = np.argwhere(np.diff(np.sign(nx))!=0).flatten()
        idx_y = np.argwhere(np.diff(np.sign(ny))!=0).flatten()
        idx_z = np.argwhere(np.diff(np.sign(nz))!=0).flatten()
        ax1.scatter3D(x[idx_x],y[idx_x],z[idx_x],c='r')
        ax1.scatter3D(x[idx_y],y[idx_y],z[idx_y],c='r')
        ax1.scatter3D(x[idx_z],y[idx_z],z[idx_z],c='r')
        idx_xx = np.argwhere(np.diff(np.sign(nxx))!=0).flatten()
        idx_yy = np.argwhere(np.diff(np.sign(nyy))!=0).flatten()
        idx_zz = np.argwhere(np.diff(np.sign(nzz))!=0).flatten()
        ax1.scatter3D(x[idx_xx],y[idx_xx],z[idx_xx],c='g')
        ax1.scatter3D(x[idx_yy],y[idx_yy],z[idx_yy],c='g')
        ax1.scatter3D(x[idx_zz],y[idx_zz],z[idx_zz],c='g')
        if b[0][-1] >= 3:
            nxxx,nyyy,nzzz,_,_,_,_ = splev(n,b[0],der=3)
            idx_xxx = np.argwhere(np.diff(np.sign(nxxx))!=0).flatten()
            idx_yyy = np.argwhere(np.diff(np.sign(nyyy))!=0).flatten()
            idx_zzz = np.argwhere(np.diff(np.sign(nzzz))!=0).flatten()
            ax1.scatter3D(x[idx_xxx],y[idx_xxx],z[idx_xxx],c='y')
            ax1.scatter3D(x[idx_yyy],y[idx_yyy],z[idx_yyy],c='y')
            ax1.scatter3D(x[idx_zzz],y[idx_zzz],z[idx_zzz],c='y')
        #ax.plot3D(x,y,z)
        #x_knot,y_knot,z_knot,_,_,_,_ = splev(b[1],b[0])
        #ax.plot3D(x_knot,y_knot,z_knot,'go')
        """
        if normals:
            nx = -1/nx
            ny = -1/ny
            nz = -1/nz
            l  = np.linalg.norm(np.array([nx,ny,nz]),axis=0)
            nx = (nx/l)*r
            ny = (ny/l)*r
            nz = (nz/l)*r
            points0 = np.array([x,y,z]).T.reshape(-1,1,3)
            points1 = np.array([x+nx,y+ny,z+nz]).T.reshape(-1,1,3)
            segments = np.concatenate([points0,points1],axis=1)
            lc = Line3DCollection(segments,color='black')
            ax.add_collection3d(lc)
        """
    plt.show()

from sympy import Point3D,Line3D,Plane,Float
def contour_collision(x1,y1,z1,nx1,ny1,nz1,r1,x2,y2,z2,nx2,ny2,nz2,r2,radius_buffer,contours,t1,t2):
    """
    d1 = x1*nx1+y1*ny1+z1*nz1
    d2 = x2*nx2+y2*ny2+z2*nz2
    length = ((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)**(1/2)
    if radius_buffer is not None:
        r1 += radius_buffer*r1
        r2 += radius_buffer*r2
    if not np.isclose(nx1,0):
        alpha = (nz1*nx2-nz2*nx1)/(ny2*nx1-ny1*nx2)
        beta  = (d1*nx2-d2*nx1)/(ny2*nx1-ny1*nx2)
        c     = ny1/nx1
        a_pt  = np.array([-d1/nx1-beta*c,beta,0])
        pt1   = np.array([x1,y1,z1])
        pt2   = np.array([x2,y2,z2])
        n_line= np.array([-(alpha*c+nz1/nx1),alpha,1])
        n_line=n_line/np.linalg.norm(n_line)
        dist1 = np.linalg.norm((pt1-a_pt)-np.dot(pt1-a_pt,n_line)*n_line)
        dist2 = np.linalg.norm((pt2-a_pt)-np.dot(pt2-a_pt,n_line)*n_line)
        print('dist1: {} r1: {}'.format(dist1,r1))
        print('dist2: {} r2: {}'.format(dist2,r2))
        if dist1 < r1 or dist2 < r2:
            return True
        else:
            return False
    elif not np.isclose(ny1,0):
        alpha = (nz1*ny2-nz2*ny1)/(nx2*ny1-nx1*ny2)
        beta  = (d1*ny2-d2*ny1)/(nx2*ny1-nx1*ny2)
        c     = nx1/ny1
        a_pt  = np.array([beta,-d1/ny1-beta*c,0])
        pt1   = np.array([x1,y1,z1])
        pt2   = np.array([x2,y2,z2])
        n_line= np.array([alpha,-(alpha*c+nz1/ny1),1])
        n_line=n_line/np.linalg.norm(n_line)
        dist1 = np.linalg.norm((pt1-a_pt)-np.dot(pt1-a_pt,n_line)*n_line)
        dist2 = np.linalg.norm((pt2-a_pt)-np.dot(pt2-a_pt,n_line)*n_line)
        print('dist1: {} r1: {}'.format(dist1,r1))
        print('dist2: {} r2: {}'.format(dist2,r2))
        if dist1 < r1 or dist2 < r2:
            return True
        else:
            return False
    else:
        return None
    """
    n = np.linspace(t1,t2)
    length = ((x2-x1)**2+(y2-y1)**2+(z2-z1)**2)**(1/2)
    if radius_buffer is not None:
        r1 += r1 + r1*radius_buffer
        r2 += r2 + r2*radius_buffer
    #print('{},{},{}'.format(x1,y1,z1))
    p1 = Point3D(Float(x1),Float(y1),Float(z1))
    p2 = Point3D(Float(x2),Float(y2),Float(z2))
    a = Plane(p1,normal_vector=(Float(nx1),Float(ny1),Float(nz1)))
    b = Plane(p2,normal_vector=(Float(nx2),Float(ny2),Float(nz2)))
    intersect = a.intersection(b)[0]
    dist1 = intersect.distance(p1)
    dist2 = intersect.distance(p2)
    p_seg1 = intersect.perpendicular_line(p1)
    p_seg2 = intersect.perpendicular_line(p2)
    pi1 = intersect.intersection(p_seg1)[0]
    pi2 = intersect.intersection(p_seg2)[0]
    line_1 = np.array([[p1.x,p1.y,p1.z],[pi1.x,pi1.y,pi1.z]])
    line_2 = np.array([[p2.x,p2.y,p2.z],[pi2.x,pi2.y,pi2.z]])
    n1_vec = np.array([[p1.x,p1.y,p1.z],[p1.x+nx1,p1.y+ny1,p1.z+nz1]])
    n2_vec = np.array([[p2.x,p2.y,p2.z],[p2.x+nx2,p2.y+ny2,p2.z+nz2]])
    #print('dist1: {} r1: {}'.format(dist1,r1))
    #print('dist2: {} r2: {}'.format(dist2,r2))
    if dist1 < r1 or dist2 < r2:
        """
        fig = plt.figure()
        x,y,z,_,_,_,_ = splev(n,contours[0])
        patch0 = Circle((0,0),r1,facecolor='y')
        patch1 = Circle((0,0),r2,facecolor='r')
        patch00 = Circle((0,0),r1+r1*radius_buffer,facecolor='y',alpha=0.2)
        patch11 = Circle((0,0),r2+r2*radius_buffer,facecolor='r',alpha=0.2)
        ax = fig.add_subplot(111,projection='3d')
        ax.plot3D(x,y,z,c='b')
        ax.scatter3D(x1,y1,z1)
        ax.scatter3D(x2,y2,z2)
        ax.plot3D(line_1[:,0],line_1[:,1],line_1[:,2],c='y')
        ax.plot3D(line_2[:,0],line_2[:,1],line_2[:,2],c='r')
        ax.plot3D(n1_vec[:,0],n1_vec[:,1],n1_vec[:,2],c='black')
        ax.plot3D(n2_vec[:,0],n2_vec[:,1],n2_vec[:,2],c='black')
        ax.set_xlim([min(x1,x2)-0.1,max(x1,x2)+0.1])
        ax.set_ylim([min(y1,y2)-0.1,max(y1,y2)+0.1])
        ax.set_zlim([min(z1,z2)-0.1,max(z1,z2)+0.1])
        ax.add_patch(patch0)
        pathpatch_2d_to_3d(patch0,z=0,normal=np.array([nx1,ny1,nz1]))
        #print(dir(patch0))
        #difs1 = (x1,y1,z1)-patch0._segment3d[0]
        pathpatch_translate(patch0,(x1,y1,z1))
        ax.add_patch(patch1)
        #difs2 = (x2,y2,z2)-patch1._segment3d[0]
        pathpatch_2d_to_3d(patch1,z=0,normal=np.array([nx2,ny2,nz2]))
        pathpatch_translate(patch1,(x2,y2,z2))
        ax.add_patch(patch00)
        #difs1 = (x1,y1,z1)-patch00._segment3d[0]
        pathpatch_2d_to_3d(patch00,z=0,normal=np.array([nx1,ny1,nz1]))
        pathpatch_translate(patch00,(x1,y1,z1))
        ax.add_patch(patch11)
        #difs2 = (x2,y2,z2)-patch11._segment3d[0]
        pathpatch_2d_to_3d(patch11,z=0,normal=np.array([nx2,ny2,nz2]))
        pathpatch_translate(patch11,(x2,y2,z2))
        plt.show()
        """
        return True
    else:
        return False

def contour_check(contours,t0,t1,radius_buffer):
    tl  = (t1 - t0)/10
    x1,y1,z1,r1,_,_,_   = splev(t0,contours[0])
    x11,y11,z11,_,_,_,_   = splev(t0+tl,contours[0])
    nx1 = x11-x1
    ny1 = y11-y1
    nz1 = z11-z1
    #nx1,ny1,nz1,_,_,_,_ = splev(t0,contours[0])
    n1  = np.array([nx1,ny1,nz1])
    #mag = np.linalg.norm(n1,axis=0)
    #nx1 = -mag/nx1
    #ny1 = -mag/ny1
    #nz1 = -mag/nz1
    x2,y2,z2,r2,_,_,_   = splev(t1,contours[0])
    x22,y22,z22,_,_,_,_   = splev(t1+tl,contours[0])
    nx2 = x22-x2
    ny2 = y22-y2
    nz2 = z22-z2
    #nx2,ny2,nz2,_,_,_,_ = splev(t1,contours[0])
    n2  = np.array([nx2,ny2,nz2])
    #mag = np.linalg.norm(n2,axis=0)
    #nx2 = -mag/nx2
    #ny2 = -mag/ny2
    #nz2 = -mag/nz2
    if np.sum(np.isclose(n1-n2,0)) > 1:
        return False
    elif np.isclose(nx1,0) and np.isclose(ny1,0):
        collision = contour_collision(x2,y2,z2,nx2,ny2,nz2,r2,x1,y1,z1,nx1,ny1,nz1,r1,radius_buffer,contours,t0,t1)
        print(collision)
        return collision
    else:
        collision = contour_collision(x1,y1,z1,nx1,ny1,nz1,r1,x2,y2,z2,nx2,ny2,nz2,r2,radius_buffer,contours,t0,t1)
        print(collision)
        return collision

def contour_check_all(interps,radius_buffer):
    sample_t = []
    n = np.linspace(0,1,200)
    for contours in interps:
        #fig = plt.figure()
        #ax = fig.add_subplot(111,projection='3d')
        tmp_t  = []
        t_list = []
        t_list = np.linspace(0,1,2*len(contours[1]))
        #x,y,z,r,_,_,_ = splev(t_list,contours[0])
        #nx,ny,nz,_,_,_,_ = splev(t_list,contours[0],der=1)
        #patches = []
        #ax.scatter3D(x,y,z)
        #ax.plot3D(x,y,z)
        #for i in range(len(t_list)):
        #    tmp_patch = Circle((0,0),r[i],facecolor='y')
        #    tmp_patch2 = Circle((0,0),r[i],facecolor='r')
        #    ax.add_patch(tmp_patch)
        #    ax.add_patch(tmp_patch2)
        #    pathpatch_2d_to_3d(tmp_patch2,z=0,normal=np.array([nx[i],ny[i],nz[i]]))
        #    if i < len(t_list) - 1:
        #        #pathpatch_2d_to_3d(tmp_patch2,z=0,normal=np.array([nx[i],ny[i],nz[i]]))
        #        pathpatch_2d_to_3d(tmp_patch,z=0,normal=np.array([x[i+1]-x[i],y[i+1]-y[i],z[i+1]-z[i]]))
        #    else:
        #        pathpatch_2d_to_3d(tmp_patch,z=0,normal=np.array([x[i]-x[i-1],y[i]-y[i-1],z[i]-z[i-1]]))
        #    pathpatch_translate(tmp_patch,(x[i],y[i],z[i]))
        #    pathpatch_translate(tmp_patch2,(x[i],y[i],z[i]))
        #plt.show()
        """
        nx,ny,nz,_,_,_,_ = splev(n,contours[0],der=1)
        nxx,nyy,nzz,_,_,_,_ = splev(n,contours[0],der=2)
        idx_x = np.argwhere(np.diff(np.sign(nx))!=0).flatten()
        idx_y = np.argwhere(np.diff(np.sign(ny))!=0).flatten()
        idx_z = np.argwhere(np.diff(np.sign(nz))!=0).flatten()
        idx_xx = np.argwhere(np.diff(np.sign(nxx))!=0).flatten()
        idx_yy = np.argwhere(np.diff(np.sign(nyy))!=0).flatten()
        idx_zz = np.argwhere(np.diff(np.sign(nzz))!=0).flatten()
        t_list.extend([i for i in idx_x if i not in t_list])
        t_list.extend([i for i in idx_y if i not in t_list])
        t_list.extend([i for i in idx_z if i not in t_list])
        t_list.extend([i for i in idx_xx if i not in t_list])
        t_list.extend([i for i in idx_yy if i not in t_list])
        t_list.extend([i for i in idx_zz if i not in t_list])
        if contours[0][-1] >= 3:
            nxxx,nyyy,nzzz,_,_,_,_ = splev(n,contours[0],der=3)
            idx_xxx = np.argwhere(np.diff(np.sign(nxxx))!=0).flatten()
            idx_yyy = np.argwhere(np.diff(np.sign(nyyy))!=0).flatten()
            idx_zzz = np.argwhere(np.diff(np.sign(nzzz))!=0).flatten()
            t_list.extend([i for i in idx_xxx if i not in t_list])
            t_list.extend([i for i in idx_yyy if i not in t_list])
            t_list.extend([i for i in idx_zzz if i not in t_list])
        t_list.insert(0,0)
        t_list.append(len(n)-1)
        t_list = n[sorted(t_list)]
        print(t_list)
        """
        start = None
        previous = False
        count = 0
        for t in t_list:
            if t == 0:
                tmp_t.append(t)
                continue
            t0 = tmp_t[-1]
            t1 = t
            collision = contour_check(contours,t0,t1,radius_buffer)
            if not collision and not previous:
                tmp_t.append(t)
            elif not collision and previous:
                print('resampling')
                t_resample = np.linspace(start,t1,4*count)
                for tt in t_resample:
                    collision = contour_check(contours,t0,tt,radius_buffer)
                    if not collision:
                        print('resample accepted')
                        tmp_t.append(tt)
                        t0 = tmp_t[-1]
                    else:
                        continue
                #m_collision = contour_check(contours,t0,t_m,radius_buffer)
                #if not m_collision:
                #    print('mid accepted')
                #    tmp_t.append(t_m)
                #else:
                #    print('mid rejected')
                #    tmp_t.append(t1)
                previous = False
                start = None
                count = 0
            elif collision and previous:
                count += 1
                continue
            else:
                #fig = plt.figure()
                x0,y0,z0,r0,_,_,_ = splev(t0,contours[0])
                nx0,ny0,nz0,_,_,_,_ = splev(t0,contours[0],der=1)
                #mag0 = np.linalg.norm([nx0,ny0,nz0])
                #nx0 = -mag0/nx0
                #ny0 = -mag0/ny0
                #nz0 = -mag0/nz0
                #mag0 = np.linalg.norm([nx0,ny0,nz0])
                x1,y1,z1,r1,_,_,_ = splev(t1,contours[0])
                nx1,ny1,nz1,_,_,_,_ = splev(t1,contours[0],der=1)
                #mag1 = np.linalg.norm([nx1,ny1,nz1])
                #nx1 = -mag1/nx1
                #ny1 = -mag1/ny1
                #nz1 = -mag1/nz1
                """
                patch0 = Circle((0,0),r0,facecolor='y')
                patch1 = Circle((0,0),r1,facecolor='r')
                patch00 = Circle((0,0),r0+r0*radius_buffer,facecolor='y',alpha=0.2)
                patch11 = Circle((0,0),r1+r1*radius_buffer,facecolor='r',alpha=0.2)
                ax = fig.add_subplot(111,projection='3d')
                ax.scatter3D(x0,y0,z0)
                ax.scatter3D(x1,y1,z1)
                ax.set_xlim([min(x0,x1)-0.1,max(x0,x1)+0.1])
                ax.set_ylim([min(y0,y1)-0.1,max(y0,y1)+0.1])
                ax.set_zlim([min(z0,z1)-0.1,max(z0,z1)+0.1])
                ax.add_patch(patch0)
                pathpatch_2d_to_3d(patch0,z=0,normal=np.array([nx0,ny0,nz0]))
                pathpatch_translate(patch0,(x0,y0,z0))
                ax.add_patch(patch1)
                pathpatch_2d_to_3d(patch1,z=0,normal=np.array([nx1,ny1,nz1]))
                pathpatch_translate(patch1,(x1,y1,z1))
                ax.add_patch(patch00)
                pathpatch_2d_to_3d(patch00,z=0,normal=np.array([nx0,ny0,nz0]))
                pathpatch_translate(patch00,(x0,y0,z0))
                ax.add_patch(patch11)
                pathpatch_2d_to_3d(patch11,z=0,normal=np.array([nx1,ny1,nz1]))
                pathpatch_translate(patch11,(x1,y1,z1))
                plt.show()
                """
                if len(tmp_t) == 1:
                    continue
                else:
                    start = tmp_t.pop(-1)
                    previous = True
                    count += 1
        if len(tmp_t) == 1:
            tmp_t.append(1)
        else:
            tmp_t[-1] = 1
        sample_t.append(tmp_t)
    return sample_t

def sv_data(interps,radius_buffer=0):
    points  = []
    radii   = []
    normals = []
    sample_t = contour_check_all(interps,radius_buffer)
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    for idx,tck in enumerate(interps):
        x,y,z,r,_,_,_    = splev(np.array(sample_t[idx]),tck[0])
        nx,ny,nz,_,_,_,_ = splev(np.array(sample_t[idx]),tck[0],der=1)
        l  = np.linalg.norm(np.array([nx,ny,nz]),axis=0)
        nx = nx/l
        ny = ny/l
        nz = nz/l
        ax.plot3D(x,y,z)
        for i in range(len(x)):
            patch = Circle((0,0),r[i],facecolor='r')
            ax.add_patch(patch)
            pathpatch_2d_to_3d(patch,z=0,normal=np.array([nx[i],ny[i],nz[i]]))
            pathpatch_translate(patch,(x[i],y[i],z[i]))
        tmp_points = np.zeros((len(x),3))
        tmp_points[:,0] = x
        tmp_points[:,1] = y
        tmp_points[:,2] = z
        points.append(tmp_points.tolist())
        tmp_normals = np.zeros((len(nx),3))
        tmp_normals[:,0] = nx
        tmp_normals[:,1] = ny
        tmp_normals[:,2] = nz
        radii.append(r.tolist())
        normals.append(tmp_normals.tolist())
    plt.show()
    return points,radii,normals

def plot_frames(frames):
    fig = plt.figure()
    ax  = fig.add_subplot(111,projection='3d')
    for idx,f in enumerate(frames):
        f = np.array(f)
        x,y,z = (f[:,0],f[:,1],f[:,2])
        ax.plot3D(x,y,z)
    plt.show()

def plot_branches(data,branches):
    fig = plt.figure()
    ax  = fig.add_subplot(111,projection='3d')
    for i,branch in enumerate(branches):
        for idx in branch:
            ax.plot3D([data[idx,0],data[idx,3]],
                      [data[idx,1],data[idx,4]],
                      [data[idx,2],data[idx,5]],label=str(i))
    plt.legend()
    plt.show()
