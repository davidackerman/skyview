from .annotation_layer import AnnotationLayer
from .img_wrapper import ij, arraylike_to_img, set_object_selection_mode
from jnius import cast

from .volume import Volume
import daisy

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

    def __create_sciview(self):
        # Launch SciView inside ImageJ
        cmd = 'sc.iview.commands.LaunchViewer'
        result = ij.command().run(cmd, True).get()
        sciview = result.getOutput('sciView')
        sciview.getFloor().setVisible(False)
        sciview.setObjectSelectionMode(set_object_selection_mode())
        return sciview
