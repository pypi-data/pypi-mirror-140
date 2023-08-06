import numpy as np
import pyvista as pv
import vtk
from .implicit.implicit import surface
from .branch_addition.check import *
from .branch_addition.close import *
from .branch_addition.basis import *
from .branch_addition.calculate_length import *
from .branch_addition.calculate_radii import *
from .branch_addition.set_root import *
from .branch_addition.add_edge import *
from .branch_addition.add_bifurcation import *
from .branch_addition.add_branches_v3 import *
from .sv_interface.get_sv_data import *
from .sv_interface.options import *
from .sv_interface.build_files import *
from copy import deepcopy
from itertools import combinations
from tqdm import tqdm

class tree:
    """
    # Data structure:
    # index: 0:2   -> proximal node coordinates
    # index: 3:5   -> distal node coordinates
    # index: 6:8   -> unit basis U (all)
    # index: 9:11  -> unit basis V (all)
    # index: 12:14 -> unit basis W (axial direction) (all)
    # index: 15,16 -> children (-1 means no child)
    # index: 17    -> parent (NA)
    # index: 18    -> proximal node index (only real edges)
    # index: 19    -> distal node index (only real edges)
    # index: 20    -> length (path length)
    # index: 21    -> radius (what are the units?)
    # index: 22    -> flow (NA)
    # index: 23    -> left bifurcation (NA)
    # index: 24    -> right bifurcation (NA)
    # index: 25    -> reduced resistance (NA)
    # index: 26    -> depth (NA)
    # index: 27    -> reduced downstream length (NA)
    # index: 28    -> root radius scaling factor (same as edge for intermediate)
    # index: 29    -> edge that subedge belongs to (if actual edge; self pointer)
    # index: 30    -> self identifying index (-1 if intermediate)
    """
    def __init__(self):
        self.parameters = {'gamma'   : 3.0,
                           'lambda'  : 2.0,
                           'mu'      : 1.0,
                           'nu'      : 3.6/100,
                           'Pperm'   : 100*1333.22,
                           'Pterm'   : 60*1333.22,
                           'Qterm'   : (0.125)/60,
                           'edge_num': 0}

        self.data = np.zeros((1,31))
        self.radius_buffer = 0.1
        self.fraction = None
        self.set_assumptions()

    def set_assumptions(self,**kwargs):
        self.homogeneous = kwargs.get('homogeneous',True)
        self.directed    = kwargs.get('directed',False)
        self.convex      = kwargs.get('convex',False)
        self.hollow      = kwargs.get('hollow',False)
        self.dimension   = kwargs.get('dimension',3)
        self.clamped_root= kwargs.get('clamped_root',False)

    def show_assumptions(self):
        print('homogeneous : {}'.format(self.homogeneous))
        print('directed    : {}'.format(self.diected))
        print('convex      : {}'.format(self.convex))
        print('hollow      : {}'.format(self.hollow))
        print('dimension   : {}'.format(self.dimension))
        print('clamped root: {}'.format(self.clamped_root))

    def set_boundary(self,boundary):
        self.boundary = boundary
        self.fraction = (self.boundary.volume**(1/3))/20

    def set_root(self,low=-1,high=0,start=None,direction=None,
                 limit_high=None,limit_low=None):
        Qterm = self.parameters['Qterm']
        gamma = self.parameters['gamma']
        nu    = self.parameters['nu']
        Pperm = self.parameters['Pperm']
        Pterm = self.parameters['Pterm']
        result = set_root(self.data,self.boundary,Qterm,
                          gamma,nu,Pperm,Pterm,self.fraction,
                          self.homogeneous,self.convex,self.directed,
                          start,direction,limit_high,limit_low,low=-1,high=0)
        self.data = result[0]
        self.sub_division_map = result[1]
        self.sub_division_index = result[2]
        self.parameters['edge_num'] = 1
        self.sub_division_map = [-1]
        self.sub_division_index = np.array([0])

    def add(self,low,high,isforest=False):
        vessel,data,sub_division_map,sub_division_index = add_branch(self,low,high,threshold_exponent=1.5,
                                                                     threshold_adjuster=0.75,all_max_attempts=40,
                                                                     max_attemps=10,sampling=20,max_skip=8,
                                                                     flow_ratio=8)
        if isforest:
            return vessel,data,sub_division_map,sub_division_index
        else:
            self.data = data
            self.parameters['edge_num'] += 2
            self.sub_division_map = sub_division_map
            self.sub_division_index = sub_division_index

    def n_add(self,n):
        for i in tqdm(range(n),desc='Adding vessels'):
            self.add(-1,0)

    def show(self,surface=False,vessel_colors='red',background_color='white',
             resolution=100,show_segments=True):
        models = []
        actors = []
        colors = vtk.vtkNamedColors()
        if show_segments:
            if self.homogeneous:
                data_subset = self.data[self.data[:,-1] > -1]
            else:
                data_subset = self.data[self.data[:,29] > -1]
            for edge in range(data_subset.shape[0]):
                center = tuple((data_subset[edge,0:3] + data_subset[edge,3:6])/2)
                radius = data_subset[edge,21]
                direction = tuple(data_subset[edge,12:15])
                vessel_length = data_subset[edge,20]
                cyl = vtk.vtkTubeFilter()
                line = vtk.vtkLineSource()
                line.SetPoint1(data_subset[edge,0],data_subset[edge,1],data_subset[edge,2])
                line.SetPoint2(data_subset[edge,3],data_subset[edge,4],data_subset[edge,5])
                cyl.SetInputConnection(line.GetOutputPort())
                cyl.SetRadius(radius)
                cyl.SetNumberOfSides(resolution)
                models.append(cyl)
                mapper = vtk.vtkPolyDataMapper()
                actor  = vtk.vtkActor()
                mapper.SetInputConnection(cyl.GetOutputPort())
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(colors.GetColor3d(vessel_colors))
                actors.append(actor)
            if surface:
                mapper = vtk.vtkPolyDataMapper()
                actor  = vtk.vtkActor()
                mapper.SetInputData(self.boundary.polydata)
                actor.SetMapper(mapper)
                actor.GetProperty().SetColor(colors.GetColor3d('blue'))
                actor.GetProperty().SetOpacity(0.5)
                actors.append(actor)
            renderer = vtk.vtkRenderer()
            renderer.SetBackground(colors.GetColor3d(background_color))

            render_window = vtk.vtkRenderWindow()
            render_window.AddRenderer(renderer)
            render_window.SetWindowName('SimVascular Vessel Network')

            interactor = vtk.vtkRenderWindowInteractor()
            interactor.SetRenderWindow(render_window)

            for actor in actors:
                renderer.AddActor(actor)

            render_window.Render()
            interactor.Start()

    def save(self,filename=None):
        if filename is None:
            tag = time.gmtime()
            filename = 'network_{}'.format(str(tag.tm_year)+
                                               str(tag.tm_mon) +
                                               str(tag.tm_mday)+
                                               str(tag.tm_hour)+
                                               str(tag.tm_min) +
                                               str(tag.tm_sec))
        os.mkdir(filename)
        file = open(filename+"/vessels.ccob",'wb')
        pickle.dump(self.data,file)
        file.close()
        file = open(filename+"/parameters.ccob",'wb')
        parameters = (self.parameters,self.fraction,self.homogeneous,self.directed,self.convex)
        pickle.dump(parameters,file)
        file.close()
        file = open(filename+"/boundary.ccob",'wb')
        pickle.dumps(self.boundary,file)
        file.close()

    def load(self,filename):
        file = open(filename+"/vessels.ccob",'rb')
        self.data = pickle.load(file)
        file.close()
        file = open(filename+"/parameters.ccob",'rb')
        self.parameters,self.fraction,self.homogeneous,self.directed,self.convex = pickle.load(file)
        file.close()
        file = open(filename+"/boundary.ccob",'rb')
        self.boundary = pickle.loads(file)
        file.close()

    def export(self,gui=True):
        interps,frames,branches = get_interpolated_sv_data(self.data)
        points,radii,normals    = sv_data(interps,radius_buffer=self.radius_buffer)
        inflow = self.data[0,22]
        build(points,radii,normals,file_options(inflow=inflow,gui=gui))

    def collision_free(self,outside_vessels):
        return no_outside_collision(self,outside_vessels)

class forest:
    def __init__(self,boundary=None,number_of_networks=1,
                 trees_per_network=[2],scale=None,start_points=None,
                 directions=None,root_lengths_high=None,
                 root_lengths_low=None):
        self.networks    = []
        self.connections = []
        self.backup      = []
        self.boundary    = boundary
        self.number_of_networks = number_of_networks
        self.trees_per_network = trees_per_network
        if isinstance(start_points,type(None)):
            start_points = [[None for j in range(trees_per_network[i])] for i in range(number_of_networks)]
        if isinstance(directions,type(None)):
            directions = [[None for j in range(trees_per_network[i])] for i in range(number_of_networks)]
        if isinstance(root_lengths_high,type(None)):
            root_lengths_high = [[None for j in range(trees_per_network[i])] for i in range(number_of_networks)]
        if isinstance(root_lengths_low,type(None)):
            root_lengths_low = [[None for j in range(trees_per_network[i])] for i in range(number_of_networks)]
        self.starting_points = start_points
        self.directions = directions
        self.root_lengths_high = root_lengths_high
        self.root_lengths_low  = root_lengths_low

    def set_roots(self,scale=None,bounds=None):
        if self.boundary is None:
            print("Need to assign boundary!")
            return
        networks = []
        connections = []
        backup = []
        for idx in range(self.number_of_networks):
            network = []
            if not isinstance(self.trees_per_network,list):
                print("trees_per_network must be list of ints"+
                      " with length equal to number_of_networks")
            for jdx in range(self.trees_per_network[idx]):
                tmp = tree()
                if self.directions[idx][jdx] is not None:
                    tmp.clamped_root = True
                tmp.set_boundary(self.boundary)
                if scale is not None:
                    tmp.parameters['Qterm'] *= scale
                if idx == 0 and jdx == 0:
                    collisions = [True]
                else:
                    collisions = [True]
                while any(collisions):
                    if bounds is None:
                        tmp.set_root(start=self.starting_points[idx][jdx],
                                     direction=self.directions[idx][jdx],
                                     limit_high=self.root_lengths_high[idx][jdx],
                                     limit_low=self.root_lengths_low[idx][jdx])
                    else:
                        print("Not implemented yet!")
                    collisions = []
                    for net in networks:
                        for t in net:
                            collisions.append(obb(t.data,tmp.data[0,:]))
                network.append(tmp)
            networks.append(network)
            connections.append(None)
            backup.append(None)
        self.networks    = networks
        self.connections = connections
        self.backup      = backup

    def add(self,number_of_branches,network_id=0,radius_buffer=0.01):
        if network_id == -1:
            exit_number = []
            active_networks = list(range(len(self.networks)))
            for network in self.networks:
                exit_number.append(network[0].parameters['edge_num'] + number_of_branches)
        else:
            exit_number = []
            active_networks = [network_id]
            exit_number.append(self.networks[network_id][0].parameters['edge_num'] + number_of_branches)
        while len(active_networks) > 0:
            for nid in active_networks:
                number_of_trees = len(self.networks[nid])
                for njd in range(number_of_trees):
                    success = False
                    while not success:
                        vessel,data,sub_division_map,sub_division_index = self.networks[nid][njd].add(-1,0,isforest=True)
                        new_vessels = np.vstack((data[vessel,:],data[-2,:],data[-1,:]))
                        repeat = False
                        for nikd in range(len(self.networks)):
                            if nikd == nid:
                                check_trees = list(range(len(self.networks[nikd])))
                                check_trees.remove(njd)
                            else:
                                check_trees = list(range(len(self.networks[nikd])))
                            for njkd in check_trees:
                                if not self.networks[nikd][njkd].collision_free(new_vessels):
                                    repeat = True
                                    break
                            if repeat:
                                break
                        if repeat:
                            continue
                        else:
                            success = True
                    self.networks[nid][njd].data = data
                    self.networks[nid][njd].parameters['edge_num'] += 2
                    self.networks[nid][njd].sub_division_map = sub_division_map
                    self.networks[nid][njd].sub_division_index = sub_division_index
                print(self.networks[nid][0].parameters['edge_num'])
                if self.networks[nid][0].parameters['edge_num'] >= exit_number[nid]:
                    active_networks.remove(nid)

    def export(self,show=True,resolution=100,final=False):
        model_networks = []
        for network in self.networks:
            model_trees = []
            for network_tree in network:
                model = []
                for edge in range(network_tree.parameters['edge_num']):
                    center = tuple((network_tree.data[edge,0:3] + network_tree.data[edge,3:6])/2)
                    radius = network_tree.data[edge,21]
                    direction = tuple(network_tree.data[edge,12:15])
                    vessel_length = network_tree.data[edge,20]
                    model.append(pv.Cylinder(radius=radius,height=vessel_length,
                                             center=center,direction=direction,
                                             resolution=resolution))
                model_trees.append(model)
            model_networks.append(model_trees)
        """
        model_connections = []
        for connections in conn:
            if connections is None:
                continue
            else:
                for c_idx in range(connections.shape[0]):
                    center = tuple((connections[c_idx,0:3] + connections[c_idx,3:6])/2)
                    radius = connections[c_idx,21]
                    direction = tuple((connections[c_idx,3:6] - connections[c_idx,0:3])/connections[c_idx,20])
                    vessel_length = connections[c_idx,20]
                    model_conn.append(pv.Cylinder(radius=radius,height=vessel_length,
                                                  center=center,direction=direction,
                                                  resolution=resolution))
        """
        if show:
            plot = pv.Plotter()
            colors = ['r','b','g','y']
            plot.set_background(color=[253,250,219])
            for model_network in model_networks:
                for color_idx, model_tree in enumerate(model_network):
                    for model in model_tree:
                        plot.add_mesh(model,colors[color_idx])
            #for c_model in model_conn:
            #    plot.add_mesh(c_model,'r')
                #if i == 0:
                #    plot.add_mesh(model[i],'r')
                #else:
                #    plot.add_mesh(model[i],'b')
            #path = plot.generate_orbital_path(n_points=100,viewup=(1,1,1))
            #plot.show(auto_close=False)
            #plot.open_gif('cco_gamma.gif')
            #plot.orbit_on_path(path,write_frames=True)
            #plot.close()
            return plot
