# main_server.py
from poc_cloud_gaming.delta_server import DeltaServer
from poc_cloud_gaming.delta_protocol import DeltaPacker

pos = [5, 5]
def game_logic(direction):
    global pos
    old_pos = list(pos)
    # Nueva posición
    new_x = max(1, min(18, pos[0] + direction[0]))
    new_y = max(1, min(8, pos[1] + direction[1]))
    pos = [new_x, new_y]
    
    return [(DeltaPacker.OBJ_EMPTY, old_pos[0], old_pos[1]), 
            (DeltaPacker.OBJ_HEAD, pos[0], pos[1]),
            (DeltaPacker.OBJ_APPLE, 15, 5)]

if __name__ == "__main__":
    DeltaServer(999).run(game_logic)