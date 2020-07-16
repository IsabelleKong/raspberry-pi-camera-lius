#!/usr/bin/python
from flask import Flask
#from flask_api import FlaskAPI 
from picamera import PiCamera
from time import sleep
import RPi.GPIO as GPIO
import time
import threading
import os

import io
import picamera
import logging
#import SocketServer
from threading import Condition
#from http import server
from picamera import PiCamera
from time import sleep
from signal import pause

camera = PiCamera()
#camera.rotation = 180
# see if security camera is currently recording
camIsRecording = False
# see if security camera preview is currently enabled
camPreviewEnabled = False
output = StreamingOutput()

# set up GPIO settings
GPIO.setmode(GPIO.BOARD)
# set pin numbers
PWMA = 
AIN2 = 
AIN1 =
STBY =
BIN2 =
BIN1 =
PWMB =
CIN2 =
CIN1 =
PWMC = 
GPIO.setup(PWMA , GPIO.OUT) # PWMA
GPIO.setup(AIN2, GPIO.OUT) # AIN2
GPIO.setup(AIN1, GPIO.OUT) # AIN1
GPIO.setup(STBY, GPIO.OUT) # STBY
GPIO.setup(BIN2, GPIO.OUT) # BIN2
GPIO.setup(BIN1, GPIO.OUT) # BIN1
GPIO.setup(PWMB, GPIO.OUT) # PWMB
GPIO.setup(CIN2, GPIO.OUT) # CIN2
GPIO.setup(CIN1, GPIO.OUT) # CIN1
GPIO.setup(PWMC, GPIO.OUT) # PWMC


def reset_pins():
    GPIO.output(PWMA, GPIO.LOW) # Set PWMA
    GPIO.output(AIN2, GPIO.LOW) # Set AIN2
    GPIO.output(AIN1, GPIO.LOW) # Set AIN1
    GPIO.output(STBY, GPIO.LOW) # Set STBY
    GPIO.output(BIN2, GPIO.LOW) # Set BIN2
    GPIO.output(BIN1, GPIO.LOW) # Set BIN1
    GPIO.output(PWMB, GPIO.LOW) # Set PWMB
    GPIO.output(CIN2, GPIO.LOW) # Set CIN1
    GPIO.output(CIN1, GPIO.LOW) # Set CIN2
    GPIO.output(PWMC, GPIO.LOW) # Set PWMC
    

app=Flask(__name__)

@app.route('/take_photo',methods=["GET"])  
def take_picture():
    timeStr = time.strftime("%Y%m%d-%H%M%S")
    camera.capture('/home/pi/Desktop/image_%s.jpeg' % timeStr)
    return "success!"

@app.route('/stop_camera',methods=["GET"])  
def stop_camera():
    camera.stop_preview()
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
    GPIO.output(STBY, GPIO.HIGH)
    time.sleep(5)
    reset_pins()
    return "success!"


@app.route('/right',methods=["GET"])  
def right():
    GPIO.output(STBY, GPIO.HIGH)
    time.sleep(5)
    reset_pins()
    return "success!"


@app.route('/forward',methods=["GET"])  
def forward():
    GPIO.output(STBY, GPIO.HIGH)
    time.sleep(5)
    reset_pins()
    return "success!"


@app.route('/reverse',methods=["GET"])  
def reverse():
    GPIO.output(STBY, GPIO.HIGH)
    time.sleep(5)
    reset_pins()
    return "success!"


@app.route('/start_camera',methods=["GET"])  
def start_camera():
    global camPreviewEnabled

    camPreviewEnabled = True
    return "success!"


@app.route('/stop_camera',methods=["GET"])  
def stop_camera():
    global camPreviewEnabled
    
    camPreviewEnabled = False
    return "success!"


def camera_preview():
    camera.start_recording(output, format='mjpg')
    address = ('', 80)
    server = StreamingServer(address, StreamingHandler)
    server.serve_forever()
            
    #finally :
    #camera.stop_recording()
    return



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
                    # do not stream frame if camPreview is not enabled
                    if not camPreviewEnabled:
                        continue
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

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
'''

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
            
    finally :
        camera.stop_recording()
'''    


if __name__=='__main__':
    #start a new thread for the camera preview
    cameraPreview = threading.Thread(target=camera_preview, args=())
    cameraPreview.start()
    app.run()
