from . import configure_jnius  # noqa
# imagej importing is order-sensitive w.r.t. imglyb/jnius
import imagej  # noqa
import sys

__fiji_directory__ = '/groups/scicompsoft/home/ackermand/Fiji.app' #  # noqa
if sys.platform == 'darwin':
    __fiji_directory__ = '/Applications/Fiji.app' 
    
# Launch ImageJ's JVM and setup classpath
ij = imagej.init(__fiji_directory__, headless=False)  # noqa
import scyjava

import imglyb.accesses
import imglyb.types
from jnius import JavaException, autoclass, PythonJavaClass, java_method

SceneryBase = autoclass('graphics.scenery.SceneryBase')
SceneryBase.xinitThreads()

import math
import numpy as np

PythonHelpers = autoclass('net.imglib2.python.Helpers')

class MakeAccessBiFunction(PythonJavaClass):
    __javainterfaces__ = ['java/util/function/BiFunction']

    def __init__(self, func):
        super(MakeAccessBiFunction, self).__init__()
        self.func = func
    
    @java_method('(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;')
    def apply(self, t, u):
        return self.func(t, u)
    
class MakeAccessFunction3(PythonJavaClass):
    __javainterfaces__ = ['kotlin/jvm/functions/Function3']

    def __init__(self, func):
        super(MakeAccessFunction3, self).__init__()
        self.func = func

    @java_method('(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;')
    def invoke(self, p1, p2, p3, p4):
        return self.func(p1, p2, p3, p4)

class MakeAccessLongFunction(PythonJavaClass):
    __javainterfaces__ = ['java/util/function/LongFunction']

    def __init__(self, func):
        super(MakeAccessLongFunction, self).__init__()
        self.func = func
    
    @java_method('(J)Ljava/lang/Object;')
    def apply(self, v):
        return self.func(v)

def chunk_index_to_slices(shape, chunk_shape, cell_index):

    chunks_xyz = tuple(
        int(math.ceil(s/sh))
        for s, sh in zip(shape, chunk_shape))[::-1]

    cell_coordinates_xyz = []
    dims = len(chunks_xyz)

    i = cell_index
    for d in range(dims):
        c = i % chunks_xyz[d]
        cell_coordinates_xyz.append(c)
        i = (i - c)//chunks_xyz[d]

    cell_coordinates = cell_coordinates_xyz[::-1]

    slices = tuple(
        slice(c*cs, (c + 1)*cs)
        for c, cs in zip(cell_coordinates, chunk_shape))

    return slices


def get_chunk(array, chunk_shape, chunk_index):

    slices = chunk_index_to_slices(array.shape, chunk_shape, chunk_index)
    return np.ascontiguousarray(array[slices])


def get_chunk_access(array, chunk_shape, index, size):

    try:

        chunk = get_chunk(array, chunk_shape, index)
        target = imglyb.accesses.as_array_access(chunk, volatile=True)
        return target

    except JavaException as e:

        print("exception    ", e)
        print("cause        ", e.__cause__)
        print("inner message", e.innermessage)
        if e.stacktrace:
            for line in e.stacktrace:
                print(line)
        raise e


def arraylike_to_img(array, chunk_shape):

    #access_generator = MakeAccessBiFunction(
    #    lambda i, s: get_chunk_access(array, chunk_shape, i, s))

    access_generator = MakeAccessLongFunction(
        lambda i: get_chunk_access(array, chunk_shape, i, 1))

    shape_xyz = array.shape[::-1]
    chunk_shape_xyz = chunk_shape[::-1]

    img = PythonHelpers.imgWithCellLoaderFromFunc(
        shape_xyz, # dims
        chunk_shape_xyz, # blockSize
        access_generator, #bifunction makeaccess-->nees to be longfunction
        imglyb.types.for_np_dtype(array.dtype, volatile=True), #T
        imglyb.accesses.as_array_access( #a
            get_chunk(array, chunk_shape, 0),
            volatile=True),
        imglyb.caches.BoundedSoftRefLoaderCache(1))  # TODO: is array access really needed here?

    return img
