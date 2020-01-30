from .annotation_layer import AnnotationLayer
from .img_wrapper import ij, MakeAccessFunction3
from .node_movement import MoveNode
#from jnius import cast
import jnius

import scyjava

from .volume import Volume
import daisy

import time

class Viewer:

    def __init__(self):

        self.volumes = {}
        self.volume_nodes = {}
        self.updated_volume_name_count=0
        self.annotation_layers = {}

        self.sciview = self.__create_sciview()

        
    def add_volume(
            self,
            name,
            array,
            chunk_shape=None,
            voxel_size=None,
            offset=None,
            lut_name=None):

        if isinstance(array, daisy.Array):

            if chunk_shape is None:
                chunk_shape = data.chunk_shape
            if voxel_size is None:
                voxel_size = data.voxel_size
            if offset is None:
                offset = data.roi.get_begin()

            array = array.data

        volume = Volume(array, chunk_shape, voxel_size, offset)
        self.volumes[name] = volume

        volume_node=self.sciview.addVolume(volume.to_img())
        
        volume_node.setName(name)
        
        
        if lut_name:
            self.sciview.setColormap(volume_node,lut_name)
        
        self.volume_nodes[name] = volume_node
                    
        return volume
    
    def update_volume(self,
            updated_array,
            name):
       self.volumes[name].data = updated_array
       volume_cast = cast('graphics.scenery.volumes.Volume', self.volume_nodes[name])
       
       self.sciview.updateVolume(self.volumes[name].to_img(),"{}".format(self.updated_volume_name_count),[250,250,250],volume_cast)
       self.updated_volume_name_count += 1
       
    def update_node(self,
            name):
       self.sciview
       self.volumes[name].data = updated_array
       volume_cast = cast('graphics.scenery.Node', self.volume_nodes[name])
       self.sciview.nodeP .updateProperties(node)
       self.sciview.updateVolume(self.volumes[name].to_img(),"{}".format(self.updated_volume_name_count),[250,250,250],volume_cast)

        #return volume

    def add_annotation_layer(self, name):

        layer = AnnotationLayer(self.sciview)
        self.annotation_layers[name] = layer

        # TODO: add to sciview

        return layer

    def set_position(self, position):
        self.sciview.moveCamera(position)

    def show(self):
        input("Press ENTER to quit...")
        self.close()

    def close(self):
        self.sciview.close()
        
    def set_object_selection_mode(self):
        return MakeAccessFunction3(
            lambda p1, raycast_result, x, y : self.do_stuff_with_selection(raycast_result, x, y))

    def do_stuff_with_selection(self,raycast_result, x, y):
        matches = scyjava.to_python(raycast_result.getMatches())
        if matches:
            closest_node = matches[ 0 ].getNode()
            self.sciview.setActiveNode(closest_node)
            h = self.sciview.publicGetInputHandler()
            
            #move with camera
#             speed_keybindings = {"slow":"", "fast":"shift ", "veryfast": "ctrl shift "}
#             direction_keybindings = {"up":"X","down":"C","left":"A","right":"D","forward":"W","back":"S"}
#             for speed in speed_keybindings:
#                 for direction in direction_keybindings:
#                     behaviour_name = "camera_and_node_move_"+direction+"_"+speed
#                     keybinding = speed_keybindings[speed]+direction_keybindings[direction]
#                     movement_command = MoveNode(self.sciview, behaviour_name)
#                     h.addBehaviour(behaviour_name, movement_command )
#                     h.addKeyBinding(behaviour_name,keybinding)
                    
            #move on own
            speed_keybindings = {"slow":"", "fast":"shift ", "veryfast": "ctrl shift "}
            direction_keybindings = {"up":"M","down":"N","left":"J","right":"L","forward":"I","back":"K"}
            for speed in speed_keybindings:
                for direction in direction_keybindings:
                    behaviour_name = "node_move_"+direction+"_"+speed
                    keybinding = speed_keybindings[speed]+direction_keybindings[direction]
                    movement_command = MoveNode(self.sciview, behaviour_name)
                    h.addBehaviour(behaviour_name, movement_command )
                    h.addKeyBinding(behaviour_name,keybinding)

        
            #self.sciview.centerOnNode(closest_node)
            material = closest_node.getMaterial()
            position = closest_node.getPosition()
            current_grayscale_color = material.diffuse.get(0)
            new_grayscale_color = 1.0
            if current_grayscale_color == 1.0:
                new_grayscale_color = 0.2
                
            color = self.sciview.getGLVector(new_grayscale_color, new_grayscale_color, new_grayscale_color)
            material.setAmbient(color)
            material.setDiffuse(color)
            material.setSpecular(color)
            

    def printGL(self, glvector, description=""):
        print("{} {}, {}, {}".format(description, glvector.get(0),glvector.get(1),glvector.get(2)))
        
    def __create_sciview(self):
        # Launch SciView inside ImageJ
        cmd = 'sc.iview.commands.LaunchViewer'
        result = ij.command().run(cmd, True).get()
        sciview = result.getOutput('sciView')
        sciview.getFloor().setVisible(False)
        
#        h = sciview.publicGetInputHandler()
#         h.removeBehaviour("select_command")
#         h.removeKeyBinding("select_command")
#        h.removeBehaviour("object_selection_mode")
#        h.removeKeyBinding("object_selection_mode")
        sciview.setObjectSelectionMode(self.set_object_selection_mode())
        
                


        return sciview
