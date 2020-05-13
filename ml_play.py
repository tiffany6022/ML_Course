"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import math

def ml_loop(side: str):
    """
    The main loop for the machine learning process
    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```
    @param side The side which this script is executed for. Either "1P" or "2P".
    """


    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    hit_blocker_side = False
    ball_80_position = 0
    block_position = []
    block_speed_x = 0

    def predict_ball(x, ball_position, ball_speed):
    # print(scene_info)
        pred = ball_position + (ball_speed*x)
        x_speed = abs(ball_speed)
        if pred < 0:
            # print("<0")
            remaining_x = x - math.ceil(ball_position / x_speed)
            pred = remaining_x * x_speed
            if pred > 195:
                remaining_x = remaining_x - math.ceil(195 / x_speed)
                pred = 195 - remaining_x * x_speed
                if pred < 0:
                    remaining_x = remaining_x - math.ceil(195 / x_speed)
                    pred = remaining_x * x_speed
        elif pred > 195:
            # print(">195")
            remaining_x = x - math.ceil((195 - ball_position) / x_speed)
            pred = 195 - remaining_x * x_speed
            if pred < 0:
                remaining_x = remaining_x - math.ceil(195 / x_speed)
                pred = remaining_x * x_speed
                if pred > 195:
                    remaining_x = remaining_x - math.ceil(195 / x_speed)
                    pred = 195 - remaining_x * x_speed
        # print(pred)
        return pred

    def predict_block(x):
        pred = scene_info["blocker"][0] + (block_speed_x*x)
        if pred < 0:
            remaining_x = x - math.ceil(scene_info["blocker"][0]/abs(block_speed_x))
            pred = remaining_x * abs(block_speed_x)
            if pred > 170:
                remaining_x = remaining_x - math.ceil(170/abs(block_speed_x))
                pred = 170 - remaining_x * abs(block_speed_x)
        elif pred > 170:
            remaining_x = x - math.ceil((170 - scene_info["blocker"][0])/abs(block_speed_x))
            pred = 170 - remaining_x * abs(block_speed_x)
            if pred < 0:
                remaining_x = remaining_x - math.ceil(170/abs(block_speed_x))
                pred = remaining_x * abs(block_speed_x)
        return pred

    def pred_hit_side():
        x = math.ceil((235-80) / scene_info["ball_speed"][1])
        ball_pred_y = 80 + x * scene_info["ball_speed"][1]
        print(f"ball_pred_y: {ball_pred_y}")
        for i in range(math.ceil(20/scene_info["ball_speed"][1])):
            ball_pred = predict_ball(x+i, scene_info["ball"][0], scene_info["ball_speed"][0])
            block_pred = predict_block(x+i)
            print(f"============ball_pred: {ball_pred}, block_pred: {block_pred}")
            if ball_pred > (block_pred-5) and ball_pred < (block_pred+30):
                hit_blocker_side = True
                ball_80_position = scene_info["ball"][0]
                print("hit_side")
                return
        hit_blocker_side = False
        return
        

    # def use_slicing():


    def move_to(player, pred) : #move platform to predicted position to catch ball 
        if player == '1P':
            # use_slicing
            # if use_slicing() and scene_info["ball"][1] < 415 and scene_info["ball"][1] >= (415-abs(scene_info["ball_speed"][1])) and scene_info["ball_speed"][1] > 0: # slicing
            #     if scene_info["ball_speed"][0] > 0 : return 1
            #     else : return 2
            pred = pred - (pred % 5) # no slicing
            if scene_info["platform_1P"][0]+15 == (pred) : return 0 # NONE
            elif scene_info["platform_1P"][0]+15 < (pred) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+20  > (pred-10) and scene_info["platform_2P"][0]+20 < (pred+10): return 0 # NONE
            elif scene_info["platform_2P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left

    def ml_loop_for_1P(): 
        if scene_info["ball"][1] >= 240 and scene_info["ball"][1] <=260 and scene_info["ball_speed"][1] > 0:
            print("ball_x: , block_x: ", scene_info["ball"][0], scene_info["blocker"][0])
            print("ball_y", scene_info["ball"][1])
        if scene_info["ball_speed"][1] > 0 : # 球正在向下 # ball goes down
            if scene_info["ball"][1] == 80: 
                pred_hit_side()
            if hit_blocker_side and scene_info["ball"][1] <= 260:
                return move_to(player = '1P',pred = ball_80_position)
            x = math.ceil(( scene_info["platform_1P"][1]-5-scene_info["ball"][1] ) / abs(scene_info["ball_speed"][1])) # 幾個frame以後會需要接  # x means how many frames before catch the ball
            pred = predict_ball(x, scene_info["ball"][0], scene_info["ball_speed"][0])
            return move_to(player = '1P',pred = pred)
        else : # 球正在向上 # ball goes up
            return move_to(player = '1P',pred = 100)



    def ml_loop_for_2P():  # as same as 1P
        if scene_info["ball_speed"][1] >= 0 : 
            return move_to(player = '2P',pred = 100)
        else : 
            x = ( scene_info["platform_2P"][1]+30-scene_info["ball"][1] ) // scene_info["ball_speed"][1] 
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x) 
            bound = pred // 200 
            if (bound > 0):
                if (bound%2 == 0):
                    pred = pred - bound*200 
                else :
                    pred = 200 - (pred - 200*bound)
            elif (bound < 0) :
                if bound%2 ==1:
                    pred = abs(pred - (bound+1) *200)
                else :
                    pred = pred + (abs(bound)*200)
            return move_to(player = '2P',pred = pred)

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False
            hit_blocker_side = False
            ball_80_position = 0
            block_position = []
            block_speed_x = 0

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information
        block_position.append(scene_info["blocker"][0])
        if len(block_position) == 2:
            block_speed_x = block_position[1] - block_position[0]
            del block_position[0]

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            # comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            comm.send_to_game({"frame": scene_info["frame"]})
            ball_served = True
        else:
            if side == "1P":
                command = ml_loop_for_1P()
            else:
                command = ml_loop_for_2P()

            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else :
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})