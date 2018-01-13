# This Python file uses the following encoding: utf-8

import sys, os, time
from math import sin, cos, tan, acos, atan, sqrt, isnan
from modules.config import res, deffile, simstep
from modules.utils import struct

degree_to_radian = 0.0174532925
radian_to_degree = 57.2957795

class Car():
    # Car class
    def __init__(self,speed=0.0,direction=0.0,acceleration=0.0,turn=0.0,x_pos=float(res[0]/2),y_pos=float(res[1]/2),max_turn=45,max_acc=10,max_brake=-40,dist=0):
        self.speed = speed
        self.direction = direction
        self.acceleration = acceleration
        self.max_acc = max_acc
        self.max_brake = max_brake
        self.turn = turn
        self.max_turn = max_turn
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.distance = dist
    
    #direct update of car parameters (a.k.a. hacking)
    def update(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    # Move car using current speed and orientation
    def move(self, acceleration, turn, step=simstep):
        # check for limits
        if acceleration < self.max_brake: acceleration = self.max_brake
        elif acceleration > self.max_acc: acceleration = self.max_acc
        if turn < -self.max_turn: turn = -self.max_turn
        elif turn > self.max_turn: turn = self.max_turn
        # update acceleration and turn
        self.acceleration = acceleration
        self.turn = turn
        # update speed and direction
        self.speed += step * self.acceleration
        self.direction = (self.direction + step * self.turn + 360)%360
        # move car
        radian = self.direction*degree_to_radian
        self.x_pos = (self.x_pos + step * self.speed * cos(radian))#%res[0]
        self.y_pos = (self.y_pos + step * self.speed * sin(radian))#%res[1]
        self.distance = self.distance + step * abs(self.speed)
        
class Track():
    # Track class
    def __init__(self,filename = None):
        # Try to load track
        if filename != None:
            filename = os.path.normpath(os.getcwd() + "/tracks/" + filename)
            try:
                self.loadFromFile(filename)
            except:
                print("Could not load track from file '" + filename + "'. Loading default track instead.")
                filename = None
        # Use default track if none was provided
        if filename == None:
            filename = os.path.normpath(os.getcwd() + "/tracks/" + deffile)
            try:
                self.loadFromFile(filename)
            except:
                print("Unexpected error. Could not load the default track. Default track file may be broken or missing. Exitting...")
                sys.exit()
        # Calculate track border points (gates)
        self.calculateGates()
        # Calculate track length
        self.calculateTrackLength()
    # Load track from file
    def loadFromFile(self,filename):
        with open(filename) as f:
            data = [line.strip().split() for line in f]
        self.point = [struct(x=float(line[0]),y=float(line[1]),width=float(line[2])) for i, line in enumerate(data)]
        self.filename = filename
    # Calculate gate parameters
    def calculateGates(self):
        left_right_switch = 0
        last_div = 0
        last_perpendicular = 0
        count = len(self.point)
        self.gate = []
        for current in range(0,count):
            current_gate = struct()
            # set current indices
            next = (current + 1) % count
            previous = (count + current - 1) % count
            # set gate line parameters (using formulas y=kx+q, k=(y2-y1)/(x2-x1) and k_perpendicular=-1/k)
            y_diff = self.point[previous].y - self.point[next].y
            x_diff = self.point[previous].x - self.point[next].x
            try: div = y_diff / x_diff
            except ZeroDivisionError: 
                if last_div >=0: div = float("inf")
                else:            div = float("-inf")
            last_div = div
            try: perpendicular = 0 - 1 / div
            except ZeroDivisionError:
                if last_perpendicular >= 0: perpendicular = float("inf")
                else:                       perpendicular = float("-inf")
            last_perpendicular = perpendicular
            current_gate.k = perpendicular
            current_gate.q = self.point[current].y - current_gate.k * self.point[current].x
            if current_gate.k == float("inf") or current_gate.k == float("-inf"):
                current_gate.q = self.point[current].x
            # set gate line angle (k=tan(angle), angle=arctan(k))
            current_gate.angle = (atan(current_gate.k) * radian_to_degree + 360)%360
            # set gate border points
            radian = current_gate.angle * degree_to_radian
            x_delta = self.point[current].width * cos(radian)
            y_delta = self.point[current].width * sin(radian)
            if y_diff < 0: left_right_switch = 0
            if y_diff > 0: left_right_switch = 1
            if left_right_switch == 0:
                current_gate.left_x = self.point[current].x + x_delta
                current_gate.left_y = self.point[current].y + y_delta
                current_gate.right_x = self.point[current].x - x_delta
                current_gate.right_y = self.point[current].y - y_delta
            else:
                current_gate.left_x = self.point[current].x - x_delta
                current_gate.left_y = self.point[current].y - y_delta
                current_gate.right_x = self.point[current].x + x_delta
                current_gate.right_y = self.point[current].y + y_delta
            # add gate to list
            self.gate.append(current_gate)
    # Return distance between gates
    def getGateDistance(self,gate1,gate2):
        gate1 = (gate1 + len(self.point)) % len(self.point)
        gate2 = (gate2 + len(self.point)) % len(self.point)
        return pointToPointDist(self.point[gate1].x, self.point[gate1].y, self.point[gate2].x, self.point[gate2].y)
    # Return track length
    def calculateTrackLength(self):
        self.length = 0
        for i in range(len(self.gate)):
            self.length += self.getGateDistance(i,i+1)

class Navigator():
    # Car navigator class (goalsetter)
    def __init__(self, track, car, start_gate = 0, switch_distance = 0, stop_distance = 10):
        self.track = track
        self.car = car
        self.start_gate = start_gate
        self.previous_gate = start_gate
        self.next_gate = start_gate + 1
        self.passed_gates = 0
        if switch_distance == 0: self.switch_distance = track.point[0].width
        else: self.switch_distance = switch_distance
        self.stop_distance = stop_distance
        self.lost = False
        self.finished = False
        self.last_distance = 0
        self.last_angle = 0
    # Navigate car to next goal
    def navigate(self):  #return [goal_distance, goal_angle]
        # car position
        A_x = self.car.x_pos
        A_y = self.car.y_pos
        # car front position
        radian = self.car.direction*degree_to_radian
        B_x = self.car.x_pos + 10 * cos(radian)
        B_y = self.car.y_pos + 10 * sin(radian)
        # next gate
        gate = self.next_gate
        # get distance to the gate
        dist = pointToPointDist(A_x,A_y,self.track.point[gate].x,self.track.point[gate].y)
        # check track completion
        if self.passed_gates > len(self.track.gate)+(1+int(self.switch_distance/dist)):
            self.finished = True
        # if distance to gate is small, go to the following gate
        while dist <= self.switch_distance:
            self.next_gate = (self.next_gate + 1)%(len(self.track.gate))
            gate = self.next_gate
            self.passed_gates += 1
            dist = pointToPointDist(A_x,A_y,self.track.point[gate].x,self.track.point[gate].y)
        # if distance is large, set stop signal
        if dist > self.stop_distance:
            self.lost = True
        # goal position
        C_x = self.track.point[gate].x
        C_y = self.track.point[gate].y
        # calculate car-front-goal triangle distances
        c = pointToPointDist(A_x,A_y,B_x,B_y)
        a = pointToPointDist(B_x,B_y,C_x,C_y)
        b = pointToPointDist(C_x,C_y,A_x,A_y)
        # set goal angle (using law of cosines)
        try:
            angle = acos((b**2+c**2-a**2)/(2.0*b*c)) * radian_to_degree
        except ValueError:
            print("Warning. Math domain error occured computing expression:")
            print("angle=acos(("+str(b)+"**2+"+str(c)+"**2-"+str(a)+"**2)/(2.0*"+str(b)+"*"+str(c)+"))*"+str(radian_to_degree))
            print("Setting angle to the last known computed value ("+str(self.last_angle)+").")
            angle = self.last_angle
        # determine on which side the goal is (left/right)
        radian = ((self.car.direction+90)%360) * degree_to_radian
        L_x = self.car.x_pos + 10 * cos(radian)
        L_y = self.car.y_pos + 10 * sin(radian)
        L_dist = pointToPointDist(C_x,C_y,L_x,L_y)
        radian = ((self.car.direction+270)%360) * degree_to_radian
        R_x = self.car.x_pos + 10 * cos(radian)
        R_y = self.car.y_pos + 10 * sin(radian)
        R_dist = pointToPointDist(C_x,C_y,R_x,R_y)
        if (L_dist < R_dist): angle = -angle
        # store and return last values
        self.last_distance = dist
        self.last_angle = angle
        return [dist, angle]
    # Return distance remaining to finish gate
    def getRemainingDistance(self):
        if self.finished == True:
            return 0
        # gates
        current = self.next_gate
        finish = self.start_gate
        # gate count
        gate_count = len(self.track.point)
        # car position
        A_x = self.car.x_pos
        A_y = self.car.y_pos
        # get distance to the next gate
        dist = pointToPointDist(A_x,A_y,self.track.point[current].x,self.track.point[current].y)
        # add distance to finish
        while current != finish:
            # get next gate
            next = (1 + current + gate_count) % gate_count
            # get gate coordinates
            curr_x = self.track.point[current].x
            curr_y = self.track.point[current].y
            next_x = self.track.point[next].x
            next_y = self.track.point[next].y
            dist += pointToPointDist(curr_x, curr_y, next_x, next_y)
            # move to the next gate
            current = next
        return dist

class Timer():
    # Simulation timer class
    def __init__(self, real_time = 0.0, simulation_time = 0.0):
        self.real_time = real_time
        self.simulation_time = simulation_time
        self._start_time = time.time()
        self._last_time = self._start_time
        self._current_time = self._start_time
    # Progress one time step
    def timeStep(self, step = simstep, fast = False):
        # wait until end of simulation step
        self._last_time = self.simulation_time
        self._current_time = time.time() - self._start_time
        if fast == False:
            time_diff = abs(self._current_time - self._last_time)
            wait_time = step - time_diff
            if wait_time <= step and wait_time > 0: time.sleep(wait_time)
        # set current simulation time
        self.simulation_time += step
        # set current real time
        self.real_time = self._current_time + step
    # Get real time
    def getRealTime(self):
        return self.real_time
    # Get simulation time
    def getSimTime(self):
        return self.simulation_time

class Clockwatch():
    # Clockwatch time counter class
    def __init__(self, start = False):
        self.is_measuring = start
        self.total_time = 0.0
        self.start_time = time.time()
    # Start measurement
    def Start(self):
        if self.is_measuring: return
        self.is_measuring = True
        self.start_time = time.time()
    # Stop measurement
    def Stop(self):
        if self.is_measuring:
            self.is_measuring = False
            self.total_time += time.time() - self.start_time
    # Reset clock
    def Reset(self):
        self.is_measuring = False
        self.total_time = 0.0
        self.start_time = time.time()
    # Restart clock
    def Restart(self):
        self.is_measuring = True
        self.total_time = 0.0
        self.start_time = time.time()
    # Get time
    def getTime(self):
        if self.is_measuring:
            return self.total_time + (time.time() - self.start_time)
        else:
            return self.total_time
    # Get formatted time string
    def getTimeString(self):
        # get total time
        t = self.getTime()
        # substract days
        days = t // 86400
        t = t % 86400
        # substract hours
        hours = t // 3600
        t = t % 3600
        # substract minutes
        minutes = t // 60
        t = t % 60
        # remaining seconds
        seconds = t
        # return formatted string
        d_s = str(int(days))
        h_s = str(int(hours))
        m_s = str(int(minutes))
        s_s = "{:.3f}".format(seconds)
        return d_s+" days, "+h_s+" hours, "+m_s+" minutes, "+s_s+" seconds"
        
class SimpleController():
    # Demonstrative controller
    def control(self, distance, angle): #return [acceleration, turn]
        trn = 0
        acc = 0
        #if target is in front speedup
        if abs(angle) < 5:
            acc += 5
        #if target is back and far, turn to it
        elif abs(angle) > 150 and distance > 30:
            trn = 90
        #if target is on left, turn to it
        if angle < -5:
            trn = 20
            acc -=5
        #if target is on right, turn to it
        elif angle > 5:
            trn = -20
            acc -= 5
        #if target is much left or right, slow down
        if abs(angle) > 50 and abs(angle) <= 150:
            acc -=10
        # return controlled values
        return [acc, trn]

class Simulator():
    # Simulator class
    def __init__(self, track, car, navigator, controller, timer):
        self.track = track
        self.car = car
        self.navigator = navigator
        self.controller = controller
        self.timer = timer
    def runSimulationStep(self, step = simstep, fast = False):
        # run navigator
        [dist,angle] = self.navigator.navigate()
        # run controller
        [acceleration, turn] = self.controller.control(dist,angle)
        # update car position
        self.car.move(acceleration, turn, step)
        # progress simulation by time step
        self.timer.timeStep(step,fast)
    def saveStats(self,statistics):
        stat = struct()
        stat.time = self.timer.getSimTime()
        stat.distance = self.car.distance
        stat.speed = self.car.speed
        stat.acceleration = self.car.acceleration
        stat.direction = self.car.direction
        stat.turn = self.car.turn
        stat.goalangle = self.navigator.last_angle
        stat.x = self.car.x_pos
        stat.y = self.car.y_pos
        statistics.append(stat)
    def aggregateStats(self,statistics):
        res = struct()
        res.avg_speed = 0
        res.avg_acc = 0
        res.avg_turn = 0
        res.avg_goalangle = 0
        for stat in statistics:
            res.avg_speed += abs(stat.speed) / float(len(statistics))
            res.avg_acc += abs(stat.acceleration) / float(len(statistics))
            res.avg_turn += abs(stat.turn) / float(len(statistics))
            res.avg_goalangle += abs(stat.goalangle) / float(len(statistics))
        res.time = statistics[-1].time
        res.distance = res.avg_speed * res.time
        res.lost = self.navigator.lost
        res.finished = self.navigator.finished
        res.remaining = self.navigator.getRemainingDistance()
        return res

# Distance between points (x1,y1) and (x2,y2)
def pointToPointDist(x1, y1, x2, y2):
    return sqrt((x1-x2)**2 + (y1-y2)**2)
