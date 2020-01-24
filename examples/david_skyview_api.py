import numpy as np
import random
import skyview as sv
from skimage import io
from time import sleep
from numpy.random.mtrand import randint

def create_volume(shape, dtype):

    volume = np.ones(shape, dtype=dtype)
    return volume

class SkyViewApplication:

    def __init__(self):

        self.viewer = sv.Viewer()
        self.annotation_texts = {}

    def handle_hover_enter(self, layer, annotation):

        print("Entering hover on annotation", annotation)

        text = layer.add_text(
            "annotation %d" % annotation.id,
            position=annotation.position)

        self.annotation_texts[annotation.id] = text

    def handle_hover_leave(self, layer, annotation):

        print("Leaving hover on annotation", annotation)

        layer.remove(self.annotation_texts[annotation.id])

    def handle_click(self, layer, annotation):

        print("Clicked on", annotation)

        if annotation.radius == 2.0:
            annotation.radius = 5.0
        else:
            annotation.radius = 2.0

if __name__ == "__main__":

    app = SkyViewApplication()
    
    #multichannel = io.imread("./mitosis_8bit.tif")
    #tczyx
    #dimensions = multichannel.shape

    lut_names = ['Red.lut','Green.lut','Blue.lut']
    #app.viewer.sciview.setColormap(volume,'Red')

    # create an annotation layer
    annotation_layer = app.viewer.add_annotation_layer("random spheres")

    # add spheres to it
    for k in range(10):
  
        annotation_layer.add_sphere(
            position=(
                k,  # t
                float(random.uniform(-10, 10)),  # z
                float(random.uniform(-10, 10)),  # y
                float(random.uniform(-10, 10))   # x
            ),
            color=(128, k*10, 243),
            radius=random.uniform(0.5, 2.5)
        )    
    
#     # register basic callbacks
    annotation_layer.register_callback(
        sv.Events.ON_HOVER_ENTER,
        lambda l, a: app.handle_hover_enter(l, a))
    annotation_layer.register_callback(
        sv.Events.ON_HOVER_LEAVE,
        lambda l, a: app.handle_hover_leave(l, a))
    annotation_layer.register_callback(
        sv.Events.ON_CLICK,
        lambda l, a: app.handle_click(l, a))

#     for current_channel in range(0,dimensions[2]):
#         #img = img[1:150,1:150,1:150]
#         # add three 3D+t volumes with different resolutions and offsets
#         current_image = multichannel[0,:,current_channel,:,:]
#         app.viewer.add_volume(
#             "Channel {}".format(current_channel),
#             current_image,
#             chunk_shape=current_image.shape,
#             voxel_size=(10,10,10),
#             lut_name=lut_names[current_channel])
#         
#     while(True): 
#         for current_time in range(0,dimensions[0]):
#             sleep(1)
#             print(current_time)
#             for current_channel in range(0,dimensions[2]):
#                 app.viewer.update_volume(multichannel[current_time,:,current_channel,:,:], "Channel {}".format(current_channel))

    # set initital viewer position
    app.viewer.set_position((0, 0, 0, 0))

    # opens viewer, blocks until closed
    app.viewer.show()
