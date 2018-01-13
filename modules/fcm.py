#!/usr/bin/python
# This Python file uses the following encoding: utf-8

class FCMcontroller():
    # FCM controller class
    def __init__(self, matrix):
        self.matrix = matrix
        self.C = [0 for x in range(8)]
    # Control method
    def control(self, distance, angle): #return [acceleration, turn]
        # matrix representation
        """             |C0|C1|C2|C3|C4|C5|C6|C7|
        Goal left   - C0|  |  |  |  |  |  |  |  |
        Goal center - C1|  |  |  |  |  |  |  |  |
        Goal right  - C2|  |  |  |  |  |  |  |  |
        Goal close  - C3|  |  |  |  |  |  |  |  |
        Goal medium - C4|  |  |  |  |  |  |  |  |
        Goal far    - C5|  |  |  |  |  |  |  |  |
        Accelerate  - C6|><|><|><|><|><|><|  |  |
        Turn        - C7|><|><|><|><|><|><|  |  |
        """
        # activations of input concepts
        self.C[0] = self.MFgoalLeft(angle)
        self.C[1] = self.MFgoalCenter(angle)
        self.C[2] = self.MFgoalRight(angle)
        self.C[3] = self.MFgoalClose(distance)
        self.C[4] = self.MFgoalMiddle(distance)
        self.C[5] = self.MFgoalFar(distance)
        # activations of output concepts
        for i in range(6):
            self.C[6] += self.matrix[6][i] * self.C[i]
        for i in range(6):
            self.C[7] += self.matrix[7][i] * self.C[i]
        # limit outputs
        if self.C[6] < -1: self.C[6] = -1.0
        elif self.C[6] > 1: self.C[6] = 1.0
        if self.C[7] < -1: self.C[7] = -1.0
        elif self.C[7] > 1: self.C[7] = 1.0
        # return outputs
        acceleration = self.MFacceleration(self.C[6])
        turn = self.MFturn(self.C[7])
        #print 'input = ' + str(distance) + ' ' + str(angle)
        #print 'output = ' + str(acceleration) + ' ' + str(turn)
        return [acceleration,turn]
    # Membership functions
    def MFgoalClose(self, val):
        a = 0.0
        b = 20.0
        res = val / (b - a) - b / (b - a)
        if res > 1: res = 1.0
        if res < 0: res = 0.0
        return res
    def MFgoalMiddle(self, val):
        val = abs(val-20.0)
        a = 0
        b = 10
        res = val / (a - b) - b / (a - b)
        if res > 1: res = 1.0
        if res < 0: res = 0.0
        return res;
    def MFgoalFar(self, val):
        a = 20.0
        b = 40.0
        res = val / (b - a) - a / (b - a)
        if res > 1: res = 1.0
        if res < 0: res = 0.0
        return res
    def MFgoalLeft(self, val):
        a = 10.0
        b = 90.0
        res = val / (b - a) - a / (b - a)
        if res > 1: res = 1.0
        if res < 0: res = 0.0
        return res
    def MFgoalCenter(self, val):
        val = abs(val)
        a = 0.0
        b = 10.0
        res = val / (a - b) - b / (a - b)
        if res > 1: res = 1.0
        if res < 0: res = 0.0
        return res
    def MFgoalRight(self, val):
        return self.MFgoalLeft(-val)
    def MFacceleration(self,val):
        return 20*val
    def MFturn(self,val):
        return 45*val

def listToMatrix(list):
    # Helper class - Convertor of list values to FCM matrix
    mat = [[0 for x in range(8)] for y in range(8)]
    i = 0;
    for x in range(6,8):
        for y in range(0,6):
            mat[x][y] = list[i]
            i += 1
    return mat
    