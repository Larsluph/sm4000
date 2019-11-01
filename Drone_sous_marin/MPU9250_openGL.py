#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import numpy

def acceleration_vector(ax, ay, az):
    glBegin(GL_LINES)
    # glColor3ub(0, 0, 0)
    glVertex3fv((0, 0, 0))
    glVertex3fv((ax, ay, az))
    glEnd()

def axes():
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex3fv((0, 0, 0))
    glVertex3fv((2, 0, 0))
    glEnd()
    glBegin(GL_LINES)
    glColor3ub(0, 0, 255)
    glVertex3fv((0, 0, 0))
    glVertex3fv((0, 2, 0))
    glEnd()
    glBegin(GL_LINES)
    glColor3ub(0, 255, 0)
    glVertex3fv((0, 0, 0))
    glVertex3fv((0, 0, 2))
    glEnd()

# def cube():
#     hauteur = 0.2
#     verticies = ((1, -1, -hauteur),(1, 1, -hauteur),(-1, 1, -hauteur),(-1, -1, -hauteur),(1, -1, hauteur),(1, 1, hauteur),(-1, -1, hauteur),(-1, 1, hauteur))
#
#     edges = ((0,1),(0,3),(0,4),(2,1),(2,3),(2,7),(6,3),(6,4),(6,7),(5,1),(5,4),(5,7))
#
#     glBegin(GL_LINES)
#     glColor3ub(255, 255, 0)
#     for edge in edges:
#         for vertex in edge:
#             glVertex3fv(verticies[vertex])
#     glEnd()

def cube():
    hauteur = 0.2
    verticies = ((1, -1, -hauteur),(1, 1, -hauteur),(-1, 1, -hauteur),(-1, -1, -hauteur),(1, -1, hauteur),(1, 1, hauteur),(-1, -1, hauteur),(-1, 1, hauteur))

    edges = ((0,1),(0,3),(0,4),(2,1),(2,3),(2,7),(6,3),(6,4),(6,7),(5,1),(5,4),(5,7))

    surfaces = (
    (0,1,2,3),
    (3,2,7,6),
    (6,7,5,4),
    (4,5,1,0),
    (1,5,7,2),
    (4,0,3,6)
    )

    colors = (
    (1,0,0),
    (0,1,0),
    (0,0,1),
    (0,1,0),
    (1,1,1),
    (0,1,1),
    (1,0,0),
    (0,1,0),
    (0,0,1),
    (1,0,0),
    (1,1,1),
    (0,1,1),
    )

    glBegin(GL_QUADS)
    for surface in surfaces:
        x = 0
        for vertex in surface:
            x+=1
            if surface == (4,5,1,0):
                glColor3fv([255,0,0])
            else:
                glColor3fv(colors[x])
            glVertex3fv(verticies[vertex])
    glEnd()

def display():
    global qw, qx, qy, qz
    # Clear the color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    gluLookAt(0, 10, 0, 0, 0, 0, 0, 0, 1)

    axes()
    glRotatef(2 * math.acos(qw) * 180 / math.pi, qx, qy, qz)
    # glRotatef(2 * math.acos(qw) * 180 / math.pi, -qx, -qy, -qz)
    # glRotatef(yaw, 0, 0, 1)
    cube()
    # acceleration = numpy.dot(quaternion_to_matrix(qw, -qx, -qy, -qz), numpy.array([ax, ay, az]))
    # print(acceleration)
    # acceleration_vector(-ax, -ay, -az)
    # print(yaw)
    # print(math.sqrt(ax**2 + ay**2 + az**2))
    # print(ax, ay, az)
    # print(mx)

    glFlush()
    glutSwapBuffers()

def animation():
    # data = MPU_9250.get_raw_data(port)
    # MPU_9250.t = data[0]
    # MPU_9250.ax, MPU_9250.ay, MPU_9250.az = data[1] * MPU_9250.aRes, data[2] * MPU_9250.aRes, data[3] * MPU_9250.aRes
    # MPU_9250.gx, MPU_9250.gy, MPU_9250.gz = data[4] * MPU_9250.gRes, data[5] * MPU_9250.gRes, data[6] * MPU_9250.gRes
    # MPU_9250.mx, MPU_9250.my, MPU_9250.mz = (data[7] - MPU_9250.mag_bias[0]) * MPU_9250.magCalibration[0] * MPU_9250.mRes, (data[8] - MPU_9250.mag_bias[1]) * MPU_9250.magCalibration[1] * MPU_9250.mRes, (data[9] - MPU_9250.mag_bias[2]) * MPU_9250.magCalibration[2] * MPU_9250.mRes
    #
    # MPU_9250.qw, MPU_9250.qx, MPU_9250.qy, MPU_9250.qz = quaternion_filters.mahony_Q6_Update(MPU_9250.ax, MPU_9250.ay, MPU_9250.az, MPU_9250.gx * math.pi / 180, MPU_9250.gy * math.pi / 180, MPU_9250.gz * math.pi / 180, MPU_9250.t)
    # MPU_9250.heading = MPU_9250.compute_Compass_Heading(MPU_9250.mx, MPU_9250.my)
    # print(MPU_9250.heading)

    # q = MPU_9250.mahonyQuaternionUpdate(data, [qw, qx, qy, qz], 0.01)
    # q = MPU_9250.madgwickQuaternionUpdate(data, [qw, qx, qy, qz], 0.01)
    # q = MPU_9250.original_madgwickQuaternionUpdate(data, [qw, qx, qy, qz], t, b, w_b)


    # qw, qx, qy, qz = q[0], q[1], q[2], q[3]
    # # pitch, roll, yaw = data[14], data[15], data[16]
    # print(mx, my, mz)

    # qw, qx, qy, qz = euler_to_quaternion(pitch/180*math.pi, roll/180*math.pi, yaw/180*math.pi)

    # roll, pitch, yaw = quaternion_to_euler(qw, qx, qy, qz)

    # pitch = math.atan(ay / math.sqrt(ay**2 + az**2))
    # roll = math.atan(ax / math.sqrt(ax**2 + az**2))
    #
    # xh = mx * math.cos(pitch) + my * math.sin(pitch) * math.cos(roll) + mz * math.sin(pitch) * math.cos(roll)
    # yh = my * math.cos(roll) + mz * math.sin(pitch)
    # yaw = math.atan(-yh / xh)

    # time.sleep(0.05)
    glutPostRedisplay()


ax, ay, az = 0, 0, 0
gx, gy, gz = 0, 0, 0
mx, my, mz = 0, 0, 0
qw, qx, qy, qz = 1, 0, 0, 0
t = 0
b = [1, 0]
w_b = [0, 0, 0]
pitch, roll, yaw = 0, 0, 0

def main():
    glutInit(sys.argv)

    # Create a double-buffer RGBA window.   (Single-buffering is possible.
    # So is creating an index-mode window.)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(800, 600)

    # Create a window, setting its title
    glutCreateWindow(b'Rotating cube')
    #
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 800/600, 0.1, 50.0)

    glEnable(GL_DEPTH_TEST)

    # Set the display callback.  You can set other callbacks for keyboard and
    # mouse events.

    glutDisplayFunc(display)
    glutIdleFunc(animation)
    glutPostRedisplay()

    # Run the GLUT main loop until the user closes the window.
    glutMainLoop()
