# -*-coding:utf-8 -*-

"""
 Created by Wonseok Jung in KETI on 2021-03-16.
"""

import socket, serial
import time, os
import serial

# import mavlink

_server = None

socket_mav = None
mavPort = None

mavPortNum = '/dev/ttyAMA0'
mavBaudrate = '57600'

mavstr = None


# from http_app import my_drone_type


def tas_ready():
    global _server
    global mavPortNum
    global mavBaudrate

    if my_drone_type == 'dji':
        if _server is None:
            pass
            """TBD socket connect with DJI"""
            # _server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # print('socket connected')
    elif my_drone_type == 'pixhawk':
        mavPortNum = 'COM4'
        mavBaudrate = '57600'
        mavPortOpening()


def mavPortOpening():
    global mavPort
    global mavPortNum
    global mavBaudrate

    try:
        if mavPort is None:
            mavPort = serial.Serial(mavPortNum, int(mavBaudrate), timeout=10)
            mavPortOpen()
        else:
            if mavPort.isOpen():
                pass
            else:
                mavPort.open()

    except Exception as e:
        mavPortError(e)


def mavPortOpen():
    global mavPort

    print('mavPort open. ' + mavPortNum + ' Data rate: ' + mavBaudrate)


def mavPortClose():
    global mavPort

    print('mavPort closed..')
    mavPort.close()


def mavPortError(error):
    global mavPort

    print('[mavPort error]: {}'.format(error))


def mavPortData():
    global mavPort

    mavstr = mavPort.readline()
    print(mavstr)


if __name__ == '__main__':

    my_drone_type = 'pixhawk'
    tas_ready()

    while True:
        mavPortData()

