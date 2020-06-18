import pickle
import os
import numpy as np

class MLPlay:
    def __init__(self, player):
        self.player = player
        if self.player == "player1":
            self.player_no = 0
        elif self.player == "player2":
            self.player_no = 1
        elif self.player == "player3":
            self.player_no = 2
        elif self.player == "player4":
            self.player_no = 3
        self.car_vel = 0
        self.car_pos = ()
        self.beforeCmd = 3  # SPEED only
        # with open(os.path.join(os.path.dirname(__file__),'save','SVM.pickle'), 'rb') as f:
        # with open(os.path.join(os.path.dirname(__file__),'save','KNN.pickle'), 'rb') as f:
        with open(os.path.join(os.path.dirname(__file__),'save','DecisionTree.pickle'), 'rb') as f:
        # with open(os.path.join(os.path.dirname(__file__),'save','RandomForest.pickle'), 'rb') as f:
            self.model_player = pickle.load(f)
        pass


    def update(self, scene_info):
        """
        Generate the command according to the received scene information
        """
        if scene_info["status"] != "ALIVE":
            return "RESET"

        if scene_info["frame"] <= 150:
            self.beforeCmd = 3
            return ["SPEED"]
            
        for car in scene_info["cars_info"]:
            if car["id"]==self.player_no:
                self.car_vel = car["velocity"]

        has_car = False
        # make grid
        front_car = 0
        distance_x = 1000
        distance_y = 1000
        grid = [0] * 20
        for car in scene_info["cars_info"]:
            if car["id"] == self.player_no:
                has_car = True
                pos_x = car["pos"][0]
                pos_y = car["pos"][1]
                mylane = pos_x // 70
                drive_direction = (pos_x % 70) - 35
                grid[12] = car["velocity"]
                if mylane == 0:
                    grid[0] = 15
                    grid[5] = 15
                    grid[10] = 15
                    grid[15] = 15
                    grid[1] = 15
                    grid[6] = 15
                    grid[11] = 15
                    grid[16] = 15
                elif mylane == 1:
                    grid[0] = 15
                    grid[5] = 15
                    grid[10] = 15
                    grid[15] = 15
                elif mylane == 7:
                    grid[4] = 15
                    grid[9] = 15
                    grid[14] = 15
                    grid[19] = 15
                elif mylane == 8:
                    grid[3] = 15
                    grid[8] = 15
                    grid[13] = 15
                    grid[18] = 15
                    grid[4] = 15
                    grid[9] = 15
                    grid[14] = 15
                    grid[19] = 15
                break
        if not has_car:
            return []
        for car in scene_info["cars_info"]:
            if car["id"] != self.player_no:
                lane = car["pos"][0] // 70
                diff_y = pos_y - car["pos"][1] # if positive, my car is behind
                if lane == mylane:       # same lane 
                    if diff_y > 200 and diff_y <= 400:
                        grid[2] = car["velocity"]
                        front_car = 1
                        if distance_y > diff_y:
                            distance_y = diff_y
                    elif diff_y > 80 and diff_y <= 200:
                        grid[7] = car["velocity"]
                        front_car = 1
                        if distance_y > diff_y:
                            distance_y = diff_y
                    elif diff_y > -80 and diff_y <= 80: # if ALIVE, might be other player's car
                        if drive_direction >= 0:
                            grid[11] = car["velocity"]
                        elif drive_direction < 0:
                            grid[13] = car["velocity"]
                        if abs(distance_x) > abs(pos_x - car["pos"][0]):
                            distance_x = pos_x - car["pos"][0]
                        print("boom")
                    elif diff_y > -160 and diff_y <= -80:
                        grid[17] = car["velocity"]
                elif lane == mylane - 1: # left
                    if diff_y > 200 and diff_y <= 400:
                        grid[1] = car["velocity"]
                    elif diff_y > 80 and diff_y <= 200:
                        grid[6] = car["velocity"]
                    elif diff_y > -80 and diff_y <= 80:
                        grid[11] = car["velocity"]
                        if abs(distance_x) > abs(pos_x - car["pos"][0]):
                            distance_x = pos_x - car["pos"][0]
                    elif diff_y > -160 and diff_y <= -80:
                        grid[16] = car["velocity"]
                elif lane == mylane + 1: # right
                    if diff_y > 200 and diff_y <= 400:
                        grid[3] = car["velocity"]
                    elif diff_y > 80 and diff_y <= 200:
                        grid[8] = car["velocity"]
                    elif diff_y > -80 and diff_y <= 80:
                        grid[13] = car["velocity"]
                        if abs(distance_x) > abs(pos_x - car["pos"][0]):
                            distance_x = pos_x - car["pos"][0]
                    elif diff_y > -160 and diff_y <= -80:
                        grid[18] = car["velocity"]
                elif lane == mylane - 2: # left left
                    if diff_y > 200 and diff_y <= 400:
                        grid[0] = car["velocity"]
                    elif diff_y > 80 and diff_y <= 200:
                        grid[5] = car["velocity"]
                    elif diff_y > -80 and diff_y <= 80:
                        grid[10] = car["velocity"]
                    elif diff_y > -160 and diff_y <= -80:
                        grid[15] = car["velocity"]
                elif lane == mylane + 2: # right right
                    if diff_y > 200 and diff_y <= 400:
                        grid[4] = car["velocity"]
                    elif diff_y > 80 and diff_y <= 200:
                        grid[9] = car["velocity"]
                    elif diff_y > -80 and diff_y <= 80:
                        grid[14] = car["velocity"]
                    elif diff_y > -160 and diff_y <= -80:
                        grid[19] = car["velocity"]
        # x = [front_car, drive_direction, distance_x, distance_y, self.beforeCmd, grid[0], grid[1], grid[2], grid[3], grid[4], grid[5], grid[6], grid[7], grid[8], grid[9], grid[10], grid[11], grid[12], grid[13], grid[14], grid[15], grid[16], grid[17], grid[18], grid[19]]
        x = [front_car, drive_direction, distance_x, distance_y, grid[0], grid[1], grid[2], grid[3], grid[4], grid[5], grid[6], grid[7], grid[8], grid[9], grid[10], grid[11], grid[12], grid[13], grid[14], grid[16], grid[18]]
        x = np.array(x).reshape((1,-1))
        pred = self.model_player.predict(x)
        pred = int(pred[0])
        self.beforeCmd = pred
        print(pred)

        # need to slow down
        if distance_y < 100:
            print(distance_y)
            if pred == 0 or pred == 1 or pred == 2:
                if not (grid[13] != 0 and distance_x < 0 and abs(distance_x) <= 43):  # can go right
                    return ["MOVE_RIGHT", "BRAKE"]
            elif pred == 6 or pred == 7 or pred == 8:
                if not (grid[11] != 0 and distance_x > 0 and abs(distance_x) <= 43):  # can go left
                    return ["MOVE_LEFT", "BRAKE"]
            return ["BRAKE"]
        elif distance_y < 130:
            print(distance_y)
            if pred == 0 or pred == 1 or pred == 2:
                if not (grid[13] != 0 and distance_x < 0 and abs(distance_x) <= 43):  # can go right
                    return ["MOVE_RIGHT"]
            elif pred == 6 or pred == 7 or pred == 8:
                if not (grid[11] != 0 and distance_x > 0 and abs(distance_x) <= 43):  # can go left
                    return ["MOVE_LEFT"]
            return [None]

        if pred == 0:
            if grid[13] != 0 and distance_x < 0 and abs(distance_x) <= 43:  # cannot go right
                return ["SPEED"]
            return ["MOVE_RIGHT", "SPEED"]
        elif pred == 1:
            if grid[13] != 0 and distance_x < 0 and abs(distance_x) <= 43:  # cannot go right
                return [None]
            return ["MOVE_RIGHT"]
        elif pred == 2:
            if grid[13] != 0 and distance_x < 0 and abs(distance_x) <= 43:  # cannot go right
                return ["BRAKE"]
            return ["MOVE_RIGHT", "BRAKE"]
        elif pred == 3:
            return ["SPEED"]
        elif pred == 4:
            return [None]
        elif pred == 5:
            return ["BRAKE"]
        elif pred == 6:
            if grid[11] != 0 and distance_x > 0 and abs(distance_x) <= 43:  # cannot go left
                return ["SPEED"]
            return ["MOVE_LEFT", "SPEED"]
        elif pred == 7:
            if grid[11] != 0 and distance_x > 0 and abs(distance_x) <= 43:  # cannot go left
                return [None]
            return ["MOVE_LEFT"]
        elif pred == 8:
            if grid[11] != 0 and distance_x > 0 and abs(distance_x) <= 43:  # cannot go left
                return ["BRAKE"]
            return ["MOVE_LEFT", "BRAKE"]


    def reset(self):
        """
        Reset the status
        """
        pass
