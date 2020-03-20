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
        position.append(scene_info.ball)
        if len(position) == 2:
            speed_x = position[1][0] - position[0][0]
            speed_y = position[1][1] - position[0][1]
            del position[0]
        ball_down = speed_y > 0
        if scene_info.ball[1] > random.randint(150,200) and (not have_end_posx) and abs(speed_x) >= 7:
            if not ball_down:
                continue
            move_times = math.ceil((395-scene_info.ball[1])/7)
            if speed_x > 0:    # right
                end_posx = 195 - (move_times - math.ceil((195 - scene_info.ball[0]) / abs(speed_x))) * abs(speed_x) # RL
                if end_posx < 0:
                    end_posx = ((move_times - math.ceil((195 - scene_info.ball[0]) / abs(speed_x))) - math.ceil(195 / abs(speed_x))) * abs(speed_x) # RLR            
            elif speed_x < 0:  # left
                end_posx = (move_times - math.ceil(scene_info.ball[0] / abs(speed_x))) * abs(speed_x) # LR
                if end_posx > 195:
                    end_posx = 195 - ((move_times - math.ceil(scene_info.ball[0] / abs(speed_x))) - math.ceil(195 / abs(speed_x))) * abs(speed_x) #LRL
            have_end_posx = True
            if random.randint(0,1):
                end_posx = end_posx + 5 - end_posx % 5  # platform moves +-5
           
        # old-version existing bugs 
        '''
        if scene_info.ball[1] >= 143 and scene_info.ball[1] < 150: #! if speed == 10, there is a bug
            last_posx = scene_info.ball[0]
        if scene_info.ball[1] >= 150 and scene_info.ball[1] < 157:
            now_posx = scene_info.ball[0]
            ball_down = not ball_down
            if not ball_down:
                continue
            speed = now_posx - last_posx  #! if posx == 0 or 195, there is a bug.
            move_times = math.ceil((395-scene_info.ball[1])/7)
            if speed > 0:  # right
                end_posx = 195 - (move_times - math.ceil((195 - now_posx) / abs(speed))) * abs(speed) # RL
                if end_posx < 0:
                    end_posx = ((move_times - math.ceil((195 - now_posx) / abs(speed))) - math.ceil(195 / abs(speed))) * abs(speed) # RLR
            elif speed < 0:  # left
                end_posx = (move_times - math.ceil(now_posx / abs(speed))) * abs(speed) # LR
                if end_posx > 195:
                    end_posx = 195 - ((move_times - math.ceil(now_posx / abs(speed))) - math.ceil(195 / abs(speed))) * abs(speed) #LRL
            have_end_posx = True
            # end_posx = end_posx + 5 - end_posx % 5  # platform moves +-5
        '''

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            if random.randint(0,1):
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