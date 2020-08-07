#!/usr/bin/python
from flask import Flask, Response, jsonify 
from picamera import PiCamera
from time import sleep
import RPi.GPIO as GPIO
import time
import threading
import os
import sys
sys.path.append('/usr/local/lib/python2.7/site-packages')
import cv2

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


def gen(output):
    
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame

            '''
            # do not stream frame if camPreview is not enabled
            if not camPreviewEnabled:
                break
            '''
            yield (b'--FRAME\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
'''
def gen():
    cam = cv2.VideoCapture(0)
    while True:
        ret, img = cam.read()
        
        if ret:
            frame = cv2.imencode('.jpg', img)[1].tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
             break
     
'''    
@app.route('/stream.mjpg', methods=["GET"])
def camera_preview():
    global camPreviewEnabled
    
    if camPreviewEnabled:
        output = StreamingOutput()
        camera.start_recording(output, format='mjpeg')
        resp = Response(gen(output), mimetype='multipart/x-mixed-replace; boundary=frame')
        return resp
'''
class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length',len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


'''
class StreamingOutput(object):
    
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)



class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__=='__main__':
    #start a new thread for the camera preview
    #cameraPreview = threading.Thread(target=camera_preview, args=())
    #cameraPreview.start()


    app.run()
