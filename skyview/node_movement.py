from . import configure_jnius  # noqa
import scyjava
from jnius import JavaException, autoclass, PythonJavaClass, java_method

import math
import numpy as np

class MoveNode(PythonJavaClass):
    __javainterfaces__ = ['org.scijava.ui.behaviour.ClickBehaviour']

    def __init__(self, sciview, direction):
        super(MoveNode, self).__init__()
        self.sciview = sciview
        self.direction = direction
        self.camera = sciview.getCamera()
        self.active_node = sciview.getActiveNode()
        self.speed = 1 # sciview hardcoded fast speed
        if "slow" in direction:
            self.speed = self.sciview.getFPSSpeed()
        elif "veryfast" in direction:
            self.speed = 100 # sciview hardcoded veryfast speed

        
    def v_plus(self, v1, v2):
        return self.sciview.getGLVector(v1.get(0)+v2.get(0), v1.get(1)+v2.get(1),v1.get(2)+v2.get(2))
    
    def v_minus(self, v1, v2):
        return self.sciview.getGLVector(v1.get(0)-v2.get(0), v1.get(1)-v2.get(1),v1.get(2)-v2.get(2))
    
    def v_cross_normalized(self, v1, v2):
        c_1 = v1.get(1)*v2.get(2) - v1.get(2)*v2.get(1) 
        c_2 = v1.get(2)*v2.get(0) - v1.get(0)*v2.get(2)
        c_3 = v1.get(0)*v2.get(1) - v1.get(1)*v2.get(0)
        mag = math.sqrt(c_1*c_1 + c_2*c_2 + c_3 * c_3)
        return self.sciview.getGLVector(c_1/mag, c_2/mag, c_3/mag)
        
    def v_multiply_c(self, v, c):
        return self.sciview.getGLVector(v.get(0)*c, v.get(1)*c, v.get(2)*c)

    def v_add_c(self, v,c):
        return self.sciview.getGLVector(v.get(0)+c, v.get(1)+c, v.get(2)+c)
    
    def set_movement_behavior(self):
        current_node_position = self.active_node.getPosition()
        camera_up = self.camera.getUp()
        camera_forward = self.camera.getForward()
        cross_product = self.v_cross_normalized(camera_forward, camera_up)
        dist = self.speed * self.camera.getDeltaT()
        new_node_position = 0
        if "forward" in self.direction:
            new_node_position = self.v_plus(current_node_position, self.v_multiply_c(camera_forward, dist))
        elif "back" in self.direction:
            new_node_position = self.v_minus(current_node_position, self.v_multiply_c(camera_forward, dist))
        elif "left" in self.direction:
            new_node_position = self.v_minus(current_node_position, self.v_multiply_c(cross_product, dist))
        elif "right" in self.direction:
            new_node_position = self.v_plus(current_node_position, self.v_multiply_c(cross_product, dist))
        elif "up" in self.direction:
            new_node_position = self.v_plus(current_node_position, self.v_multiply_c(camera_up, dist))
        elif "down" in self.direction:
            new_node_position = self.v_plus(current_node_position, self.v_multiply_c(camera_up, -1*dist))
        self.active_node.setPosition(new_node_position)   
            
                
    @java_method('(II)V')
    def click(self,x,y):
        self.set_movement_behavior()