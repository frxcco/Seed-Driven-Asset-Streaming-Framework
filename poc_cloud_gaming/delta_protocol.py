import struct

class DeltaPacker:
    # IDs de objetos
    OBJ_EMPTY = 0
    OBJ_HEAD = 1
    OBJ_APPLE = 2
    OBJ_WALL = 3

    @staticmethod
    def pack_delta(obj_id, x, y):
        return struct.pack("BBB", obj_id, x, y)

    @staticmethod
    def unpack_delta(data):
        return struct.unpack("BBB", data)