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
i = 0

app=Flask(__name__)

@app.route('/take_photo',methods=["POST"])  
def take_picture():
    global i
    i = i + 1
    camera.capture('/home/pi/Desktop/image_%s.jp' % i)
    return "success!"

@app.route('/stop_camera',methods=["POST"])  
def stop_camera():
    camera.stop_preview()
    return "success!"

    
@app.route('/start_recording',methods=["POST"])  
def start_recording():
    global camIsRecording
    global i
    i = i + 1

    camera.start_recording('/home/pi/Desktop/video_%s.h264' % i)
    camIsRecording = True
    return "success!"


@app.route('/stop_recording',methods=["POST"])  
def stop_recording():   
    if camIsRecording:
        camera.stop_recording()
        camIsRecording = False
    return "success!"

def camera_preview():
    return

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

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
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

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True
    


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
    camera_preview.start()
    app.run()
