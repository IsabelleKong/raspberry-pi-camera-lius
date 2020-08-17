#!/usr/bin/python
from flask import Flask, Response, jsonify 
from picamera import PiCamera
from time import sleep
import RPi.GPIO as GPIO
import time
import threading
import os
import sys


import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
from picamera import PiCamera
from time import sleep
from signal import pause


print("START")


camera = PiCamera()
print("start code")
#camera.rotation = 180
# see if security camera is currently recording
camIsRecording = False
# see if security camera preview is currently enabled
camPreviewEnabled = True
data = {"status": "ok"}

print("camera setup")

# set up GPIO settings
#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)
GPIO.setmode (GPIO.BCM)
GPIO.setup(16,GPIO.OUT)

motor1=13 #pin in motor 1
motor2=12 #pin in motor 2
motorCommand = ''

print("gpio setup1")

GPIO.setup(motor1,GPIO.OUT)
pwm1= GPIO.PWM(motor1,1000)
pwm1.start(0)



GPIO.setup(motor2,GPIO.OUT)
pwm2= GPIO.PWM(motor2,1000)
pwm2.start(0)

print("gpio setup2")


def motor_starting():
    for i in range(0,100):
        print(str(i))
        pwm1.ChangeDutyCycle(i)
        pwm2.ChangeDutyCycle(i)
        sleep(0.1)       
   

def stop1():
    print("STOP1")
    pwm1.ChangeDutyCycle(40)
    return

def maju1():
    print("MAJU1")
    pwm1.ChangeDutyCycle(90)
    return
    
def stop2():
    print("STOP2")
    pwm2.ChangeDutyCycle(40)
    return
 
def maju2():
    print("MAJU2")
    pwm2.ChangeDutyCycle(99)
    return
   
   
def motor():
    global motorCommand
    while True:
        sleep(0.1)
        if motorCommand=="W":
            maju1() #Untuk MAJU motor 1
            maju2() #Untuk MAJU motor 2
        elif motorCommand=="A":
            stop2() #Untuk STOP motor 2
            maju1() #Untuk MAJU motor 1
        elif motorCommand=="D":
            maju2() #Untuk MAJU motor 2
            stop1() #Untuk STOP motor 1  
        elif motorCommand=="S":
            stop1() #Untuk STOP motor 1
            stop2() #Untuk STOP motor 2
             
        elif motorCommand=="ON":       #Untuk Hidup Conveyor
            GPIO.output(16,True)
            print ("Conveyor ON")
        elif motorCommand=="OFF":      #Untuk Hidup Conveyor
            GPIO.output(16,False)
            print ("Conveyor OFF")

app=Flask(__name__)

@app.route('/take_photo',methods=["GET"])  
def take_picture():
    if camPreviewEnabled:
        camera.stop_recording()

    timeStr = time.strftime("%Y%m%d-%H%M%S")
    camera.capture('/home/pi/Desktop/image_%s.jpeg' % timeStr)
    
    if camPreviewEnabled:
        start_camera()
    return jsonify(data), 200

    
@app.route('/start_recording',methods=["GET"])  
def start_recording():
    global camIsRecording

    timeStr = time.strftime("%Y%m%d-%H%M%S")
    camera.start_recording('/home/pi/Desktop/video_%s.h264' % timeStr)
    camIsRecording = True
    return jsonify(data), 200


@app.route('/stop_recording',methods=["GET"])  
def stop_recording(): 
    global camIsRecording
   
    if camIsRecording:
        camera.stop_recording()
        camIsRecording = False
    return jsonify(data), 200


@app.route('/left',methods=["GET"])  
def left():
    global motorCommand
    motorCommand = 'A'
    return jsonify(data), 200


@app.route('/right',methods=["GET"])  
def right():
    global motorCommand
    motorCommand = 'D'
    return jsonify(data), 200

@app.route('/conveyor_on',methods=["GET"])  
def conveyor_on():
    global motorCommand
    motorCommand = 'ON'
    return jsonify(data), 200


@app.route('/conveyor_off',methods=["GET"])  
def conveyor_off():
    global motorCommand
    motorCommand = 'OFF'
    return jsonify(data), 200


@app.route('/forward',methods=["GET"])  
def forward():
    global motorCommand
    motorCommand = 'W'
    return jsonify(data), 200


@app.route('/reverse',methods=["GET"])  
def reverse():
    global motorCommand
    motorCommand = 'S'
    return jsonify(data), 200






#if __name__=='__main__':
    
 #start a new thread for the motor
motor_starting()
motor_thread = threading.Thread(target=motor, args=())
motor_thread.start()


app.run()
    
