import random
from random import randint

import pygame
import math
pygame.init()
width = 1280
height = 720
vel_decrease = 0.5 #decrease over 1 second
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True
orange = (255, 128, 0)
red = (255, 0, 0)
fps = 60

def tSAT(triangle1, triangle2):
    perpendicularStack = []
    for k in range(3):
        edgeVector = [
            triangle1[(k + 1) % 3][0] - triangle1[k][0],
            triangle1[(k + 1) % 3][1] - triangle1[k][1]
        ]
        perpendicularVector = [
            -edgeVector[1],
            edgeVector[0]
        ]
        perpendicularStack.append(perpendicularVector)

    for k in range(3):
        edgeVector = [
            triangle2[(k + 1) % 3][0] - triangle2[k][0],
            triangle2[(k + 1) % 3][1] - triangle2[k][1]
        ]
        perpendicularVector = [
            -edgeVector[1],
            edgeVector[0]
        ]
        perpendicularStack.append(perpendicularVector)

    axis = None
    minOverlap = None

    for line in perpendicularStack:
        amin, amax, bmin, bmax = None, None, None, None

        for t in triangle1:
            dot = t[0] * line[0] + t[1] * line[1]
            if amax is None or dot > amax:
                amax = dot
            if amin is None or dot < amin:
                amin = dot
        for t in triangle2:
            dot = t[0] * line[0] + t[1] * line[1]
            if bmax is None or dot > bmax:
                bmax = dot
            if bmin is None or dot < bmin:
                bmin = dot

        if amax < bmin or bmax < amin:
            return False, None
        else:
            overlap = min(amax, bmax) - max(amin, bmin)
            if minOverlap is None or overlap < minOverlap:
                minOverlap = overlap
                magnitude = math.hypot(line[0], line[1])
                axis = [line[0] / magnitude, line[1] / magnitude]

    if axis is None:
        return False, None
    MTV = [axis[0] * minOverlap, axis[1] * minOverlap]
    return True, MTV

class Shape:
    origin = []
    vertices = []
    indexes = []
    velocity = [0, 0]
    color = []
    isClicked = False
    colissionLevel = 0
    weight = 1

    def __init__(self, vertices, indexes, origin, collisionLevel, weight, color):
        self.weight = weight
        self.color = color
        self.vertices = vertices
        self.indexes = indexes
        self.colissionLevel = collisionLevel
        if(origin is None):
            oX = sum(x[0] for x in vertices)/len(vertices)
            oY = sum(y[1] for y in vertices)/len(vertices)
            self.origin = [oX, oY]
        else:
            self.origin = origin

    def printVertices(self):
        numOfFaces = len(self.indexes)//3
        for i in range(numOfFaces):
            triangle = [
                self.vertices[self.indexes[i * 3]],
                self.vertices[self.indexes[i * 3 + 1]],
                self.vertices[self.indexes[i * 3 + 2]]
            ]
            pygame.draw.polygon(screen, self.color, triangle)
        if(self.isClicked):
            pygame.draw.circle(screen, red, self.origin, 5)
            pygame.draw.circle(screen, orange, self.origin, 4)

    def isInside(self, x, y):
        n = len(self.vertices)
        inside = False
        for i in range(n):
            x1, y1 = self.vertices[i]
            x2, y2 = self.vertices[(i + 1) % n]

            if (y1 > y) != (y2 > y):
                intesect = (x2 - x1) * (y - y1) / (y2 - y1) + x1
                if intesect < x:
                    inside = not inside
        return inside

    def getOutOfBounds(self, mode = 0):         # 0 - at least one, 1 - all
        if(mode == 0):
            oOB = [0, 0, 0, 0, 0]                  # any, top, right, bottom, left
            for vertex in self.vertices:
                if vertex[1] < 0:
                    oOB[1] = 1
                    oOB[0] = 1
                if vertex[0] > width:
                    oOB[2] = 1
                    oOB[0] = 1
                if vertex[1] > height:
                    oOB[3] = 1
                    oOB[0] = 1
                if vertex[0] < 0:
                    oOB[4] = 1
                    oOB[0] = 1
            return oOB
        elif(mode == 1):
            oOB = [1, 1, 1, 1, 1]
            for vertex in self.vertices:
                if vertex[1] >= 0:
                    oOB[1] = 0
                    oOB[0] = 0
                if vertex[0] <= width:
                    oOB[2] = 0
                    oOB[0] = 0
                if vertex[1] <= height:
                    oOB[3] = 0
                    oOB[0] = 0
                if vertex[0] >= 0:
                    oOB[4] = 0
                    oOB[0] = 0
            return oOB

    def rotate(self, rotation):
        for vertex in self.vertices:
            tX = vertex[0] - self.origin[0]
            tY = vertex[1] - self.origin[1]
            vertex[0] = tX * math.cos(math.radians(rotation)) - tY * math.sin(math.radians(rotation))
            vertex[1] = tX * math.sin(math.radians(rotation)) + tY * math.cos(math.radians(rotation))
            vertex[0] += self.origin[0]
            vertex[1] += self.origin[1]

    def getIntersect(self, shapes):
        intersects = []
        numOfFaces = len(self.indexes) // 3
        otherShapes = [shape for shape in shapes if shape != self]

        for id, shape in enumerate(otherShapes):
            if shape.colissionLevel != self.colissionLevel:
                continue
            numOfFaces2 = len(shape.indexes) // 3
            found = False
            for i in range(numOfFaces):
                if found:
                    break
                triangle = [
                    self.vertices[self.indexes[i * 3]],
                    self.vertices[self.indexes[i * 3 + 1]],
                    self.vertices[self.indexes[i * 3 + 2]]
                ]
                for j in range(numOfFaces2):
                    triangle2 = [
                        shape.vertices[shape.indexes[j * 3]],
                        shape.vertices[shape.indexes[j * 3 + 1]],
                        shape.vertices[shape.indexes[j * 3 + 2]]
                    ]
                    collided, collisions = tSAT(triangle, triangle2)
                    if collided:
                        intersects.append([id, collisions])
                        found = True
                        break

        if(intersects):
            return intersects
        else:
            return None

    def moveByVector(self, x, y):
        self.origin[0] += x
        self.origin[1] += y
        for vertex in self.vertices:
            vertex[0] += x
            vertex[1] += y

    def applyVelocity(self):
        self.moveByVector(self.velocity[0], self.velocity[1])
        self.velocity[0] *= math.pow(1 - vel_decrease, 1 / fps)
        self.velocity[1] *= math.pow(1 - vel_decrease, 1 / fps)
        if(self.velocity[1] < self.weight):
            self.velocity[1] = self.weight

    def setPosition(self, x, y):
        xMove = x - self.origin[0]
        yMove = y - self.origin[1]
        self.origin[0] = x
        self.origin[1] = y
        for vertex in self.vertices:
            vertex[0] += xMove
            vertex[1] += yMove
s = [
    # Triangle
    Shape([[200, 100], [250, 0], [300, 100]],
          [0, 1, 2],
          None,
          0,
          1,
          (255, 255, 255)),

    # Rectangle
    Shape([[400, 100], [500, 100], [500, 200], [400, 200]],
          [0, 1, 2, 2, 3, 0],
          [450, 150],
          1,
          0,
          (255, 0, 0)),

    # Green Rectangle
    Shape([[600, 80], [750, 80], [750, 160], [600, 160]],
          [0, 1, 2, 2, 3, 0],
          [675, 120],
          1,
          5,
          (0, 255, 0)),

    # Pentagon
    Shape([[100, 300], [150, 250], [200, 300], [175, 350], [125, 350]],
          [0, 1, 2, 0, 2, 3, 0, 3, 4],
          [150, 320],
          1,
          1,
          (0, 0, 255)),

    # Hexagon
    Shape([[300, 350], [350, 320], [400, 350], [400, 400], [350, 430], [300, 400]],
          [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5],
          None,
          1,
          1,
          (255, 255, 0)),

    # Octagon
    Shape([[500, 320], [550, 320], [580, 350], [580, 400], [550, 430], [500, 430], [470, 400], [470, 350]],
          [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 5, 0, 5, 6, 0, 6, 7],
          [525, 370],
          1,
          1,
          (255, 0, 255)),

    # Trapezoid
    Shape([[700, 300], [800, 300], [850, 380], [750, 380]],
          [0, 1, 2, 0, 2, 3],
          [775, 340],
          1,
          1,
          (0, 255, 255)),

    # Parallelogram
    Shape([[950, 300], [1050, 300], [1030, 380], [970, 380]],
          [0, 1, 2, 0, 2, 3],
          [1000, 340],
          0,
          20,
          (200, 100, 50)),

    # Rhombus
    Shape([[1150, 300], [1200, 250], [1250, 300], [1200, 350]],
          [0, 1, 2, 0, 2, 3],
          None,
          0,
          3,
          (100, 200, 100)),

    # Star
    Shape([[600, 500], [615, 540], [660, 540], [625, 565], [640, 610], [600, 585], [560, 610], [575, 565], [540, 540], [585, 540]],
          [0, 1, 9, 1, 3, 9, 1, 2, 3, 3, 5, 9, 8, 9, 7, 5, 7, 9, 5, 6, 7, 3, 4, 5],
          [620, 570],
          1,
          1,
          (255, 215, 0))
]



lastPos = [0, 0]

for shape in s:
    shape.velocity = [0, 5]

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            screen.fill((0,0,0))

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y = pygame.mouse.get_pos()
                for shape in s:
                    if shape.isInside(x, y):
                        shape.isClicked = True
                        lastPos = [x, y]
                        s.insert(0, s.pop(s.index(shape)))
                        break

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                x, y = pygame.mouse.get_pos()
                for shape in s:

                    if shape.isClicked:
                        shape.velocity = [x - lastPos[0], y - lastPos[1]]
                        shape.isClicked = False



    screen.fill((0,100,0))

    for shape in s:
        shape.applyVelocity()

        if shape.getOutOfBounds(0)[2]:
            maxX = max(v[0] for v in shape.vertices)
            shape.moveByVector(width - maxX, 0)
            shape.velocity[0] = -abs(shape.velocity[0])
        if shape.getOutOfBounds(0)[4]:
            minX = min(v[0] for v in shape.vertices)
            shape.moveByVector(-minX, 0)
            shape.velocity[0] = abs(shape.velocity[0])

        if shape.getOutOfBounds(0)[1]:
            minY = min(v[1] for v in shape.vertices)
            shape.moveByVector(0, -minY)
            shape.velocity[1] = abs(shape.velocity[1])
        if shape.getOutOfBounds(0)[3]:
            maxY = max(v[1] for v in shape.vertices)
            shape.moveByVector(0, height - maxY)
            shape.velocity[1] = -abs(shape.velocity[1])




        intersects = shape.getIntersect(s)

        if pygame.mouse.get_pressed()[0] and shape.isClicked:
            x, y = pygame.mouse.get_pos()
            shape.velocity = [0, 0]

            if pygame.key.get_pressed()[pygame.K_q]:
                shape.rotate(-2)
            if pygame.key.get_pressed()[pygame.K_e]:
                shape.rotate(2)

            shape.moveByVector(x - lastPos[0], y - lastPos[1])

            lastPos = x, y

    for shape in reversed(s):
        shape.printVertices()


    pygame.display.flip()
    clock.tick(fps)
pygame.quit()