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


camera = PiCamera()
#camera.rotation = 180
# see if security camera is currently recording
camIsRecording = False
# see if security camera preview is currently enabled
camPreviewEnabled = True
data = {"status": "ok"}



# set up GPIO settings
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
# set pin numbers
PWMA = 22
AIN2 = 18
AIN1 = 16
#STBY = 
BIN2 = 21
BIN1 = 23
PWMB = 19
GPIO.setup(PWMA , GPIO.OUT) # PWMA
GPIO.setup(AIN2, GPIO.OUT) # AIN2
GPIO.setup(AIN1, GPIO.OUT) # AIN1
#GPIO.setup(STBY, GPIO.OUT) # STBY
GPIO.setup(BIN2, GPIO.OUT) # BIN2
GPIO.setup(BIN1, GPIO.OUT) # BIN1
GPIO.setup(PWMB, GPIO.OUT) # PWMB


def reset_pins():
    GPIO.output(PWMA, GPIO.LOW) # Set PWMA
    GPIO.output(AIN2, GPIO.LOW) # Set AIN2
    GPIO.output(AIN1, GPIO.LOW) # Set AIN1
    #GPIO.output(STBY, GPIO.LOW) # Set STBY
    GPIO.output(BIN2, GPIO.LOW) # Set BIN2
    GPIO.output(BIN1, GPIO.LOW) # Set BIN1
    GPIO.output(PWMB, GPIO.LOW) # Set PWMB
    

app=Flask(__name__)

@app.route('/take_photo',methods=["GET"])  
def take_picture():
    if camPreviewEnabled:
        camera.stop_recording()

    timeStr = time.strftime("%Y%m%d-%H%M%S")
    camera.capture('/home/pi/Desktop/image_%s.jpeg' % timeStr)
    
    if camPreviewEnabled:
        start_camera()
    return "success!"

    
@app.route('/start_recording',methods=["GET"])  
def start_recording():
    global camIsRecording

    timeStr = time.strftime("%Y%m%d-%H%M%S")
    camera.start_recording('/home/pi/Desktop/video_%s.h264' % timeStr)
    camIsRecording = True
    return "success!"


@app.route('/stop_recording',methods=["GET"])  
def stop_recording(): 
    global camIsRecording
   
    if camIsRecording:
        camera.stop_recording()
        camIsRecording = False
    return "success!"


@app.route('/left',methods=["GET"])  
def left():
    #GPIO.output(STBY, GPIO.HIGH)
    time.sleep(5)
    reset_pins()
    return "success!"


@app.route('/right',methods=["GET"])  
def right():
    #GPIO.output(STBY, GPIO.HIGH)
    time.sleep(5)
    reset_pins()
    return "success!"

@app.route('/conveyor_on',methods=["GET"])  
def conveyor_on():
    #GPIO.output(STBY, GPIO.HIGH)
    time.sleep(5)
    reset_pins()
    return "success!"


@app.route('/conveyor_off',methods=["GET"])  
def conveyor_off():
    #GPIO.output(STBY, GPIO.HIGH)
    time.sleep(5)
    reset_pins()
    return "success!"


@app.route('/forward',methods=["GET"])  
def forward():
    
    #GPIO.output(STBY, GPIO.HIGH)
    GPIO.output(AIN1,GPIO.HIGH)
    GPIO.output(AIN2,GPIO.LOW)
    GPIO.output(PWMA,GPIO.HIGH)
    GPIO.output(BIN1,GPIO.HIGH)
    GPIO.output(BIN2,GPIO.LOW)
    GPIO.output(PWMB,GPIO.HIGH)
    
    time.sleep(5)
    reset_pins()
    return "success!"


@app.route('/reverse',methods=["GET"])  
def reverse():
    #GPIO.output(STBY, GPIO.HIGH)
    GPIO.output(AIN1,GPIO.LOW)
    GPIO.output(AIN2,GPIO.HIGH)
    GPIO.output(PWMA,GPIO.HIGH)
    GPIO.output(BIN1,GPIO.LOW)
    GPIO.output(BIN2,GPIO.HIGH)
    GPIO.output(PWMB,GPIO.HIGH)
    
    time.sleep(5)
    reset_pins()
    return "success!"



@app.route('/start_camera',methods=["GET"])  
def start_camera():
    global camPreviewEnabled

    if not camPreviewEnabled:
        camPreviewEnabled = True
    return jsonify(data), 200


@app.route('/stop_camera',methods=["GET"])  
def stop_camera():
    global camPreviewEnabled
    
    if camPreviewEnabled:
        camPreviewEnabled = False
        camera.stop_recording()
    return jsonify(data), 200



if __name__=='__main__':
    #start a new thread for the camera preview
    #cameraPreview = threading.Thread(target=camera_preview, args=())
    #cameraPreview.start()


    app.run()
    
