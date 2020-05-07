"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)
import math
import random


def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    ball_down = True
    have_end_posx = False
    position = []
    speed_x = 0
    speed_y = 0

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False
            ball_down = True
            have_end_posx = False
            position = []
            speed_x = 0
            speed_y = 0

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        if scene_info.ball[1] == 395 and not speed_y == 0:
            have_end_posx = False
            continue
        brick_y = 0
        for x in range(len(scene_info.bricks)):
            if brick_y < scene_info.bricks[x][1]:
                brick_y = scene_info.bricks[x][1]
        for x in range(len(scene_info.hard_bricks)):
            if brick_y < scene_info.hard_bricks[x][1]:
                brick_y = scene_info.hard_bricks[x][1]
        # print(brick_y)
        position.append(scene_info.ball)
        if len(position) == 2:
            speed_x = position[1][0] - position[0][0]
            speed_y = position[1][1] - position[0][1]
            del position[0]
        ball_down = speed_y > 0
        if scene_info.ball[1] > random.randint(270,280) and (not have_end_posx) and ball_down:
            if not (abs(speed_x) == 7 or abs(speed_x) == 10):
                continue
            move_times = math.ceil((395-scene_info.ball[1])/7)
            # print(f"move_times:{move_times}")
            if speed_x > 0:    # right
                end_posx = scene_info.ball[0] + move_times * abs(speed_x)
                if end_posx > 195:          # RL
                    end_posx = 195 - (end_posx - 195)
                    if end_posx < 0:        # RLR
                        end_posx = abs(end_posx)
                        if end_posx >  195: # RLRL
                            end_posx = 195 - (end_posx - 195)
            elif speed_x < 0:  # left
                end_posx = scene_info.ball[0] - move_times * abs(speed_x)
                if end_posx < 0:            # LR
                    end_posx = abs(end_posx)
                    if end_posx > 195:      # LRL
                        end_posx = 195 - (end_posx - 195)
                        if end_posx <  0:   # LRLR
                            end_posx = abs(end_posx)
            have_end_posx = True
            # print(scene_info.ball, end_posx, speed_x)
            if random.randint(0,3) == 0:
                end_posx = end_posx + 5 - end_posx % 5  # platform moves +-5
            else:
                if end_posx % 5 == 0:
                    end_posx += 1

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            if random.randint(0,1) == 0:
                comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_RIGHT)
            ball_served = True
        elif have_end_posx:
            if end_posx > scene_info.platform[0]+20:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            elif end_posx < scene_info.platform[0]+20:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
        else:
            if 80 > scene_info.platform[0]:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            elif 80 < scene_info.platform[0]:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)