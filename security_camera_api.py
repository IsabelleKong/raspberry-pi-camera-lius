#!/usr/bin/python
from flask import Flask
#from flask_api import FlaskAPI 
from picamera import PiCamera
from time import sleep
import RPi.GPIO as GPIO
import time
import threading
import os

from send_email import send_email_with_video
import shutil
from distutils.dir_util import copy_tree

camera = PiCamera()
camera.rotation = 180
#camera.framerate = 15
# camera.resolution = (1920, 1080)

app=Flask(__name__) 
# counter for video number
video_num = 0
# see if security camera is currently enabled
camIsEnabled = False
# see if security camera is currently recording
camIsRecording = False

@app.route('/',methods=["GET"])  
def get_root():    
    return "Security camera api up and running!" 


@app.route('/enable_camera',methods=["POST"])  
def start_monitoring():
    global camIsEnabled

    camera.start_preview()
    camIsEnabled = True

    #start a new thread for the proximity sensor
    proximitySensor = threading.Thread(target=proximity_sensor, args=())
    proximitySensor.start()
    return "success! start monitoring"	

@app.route('/disable_camera',methods=["POST"])  
def stop_monitoring():   
    global camIsEnabled
    global camIsRecording
    global video_num

    camera.stop_preview()
    camIsEnabled = False
    if camIsRecording:
        camera.stop_recording()
        video_num += 1
        camIsRecording = False


    # Empty directory where videos are stored and move them to archive folder
    copy_tree("/home/pi/Documents/security_cam_proj/recorded_videos/", "/home/pi/Documents/security_cam_proj/archive/")
    shutil.rmtree("/home/pi/Documents/security_cam_proj/recorded_videos/")
    os.mkdir("/home/pi/Documents/security_cam_proj/recorded_videos/")
    
    return "success! stop monitoring"	


#@app.route('/start_recording',methods=["POST"])  
def start_recording():
    global camIsRecording

    if camIsEnabled and not camIsRecording:
        camera.start_recording('/home/pi/Documents/security_cam_proj/recorded_videos/test_video{}.h264'.format(video_num))
        camIsRecording = True

#@app.route('/stop_recording',methods=["POST"])  
def stop_recording():   
    global video_num
    global camIsRecording

    if camIsRecording:
        camera.stop_recording()
        camIsRecording = False

        # Start thread to convert existing file to mp4 and send email
        recipient_email = "duckyisabelle@gmail.com"
        send_email_thread = threading.Thread(target=convert_video_mp4_and_send_email, args=[recipient_email])
        send_email_thread.start()

        video_num += 1


def convert_video_mp4_and_send_email(recipient_email):
    # convert recorded file into mp4 file (running shellscript command)
    # command = "ffmpeg -r 30 -i recorded_videos/test_video{}.h264 -vcodec copy recorded_videos/test_video{}.mp4".format(video_num, video_num)
    cur_video_num = video_num       # So that number don't change while processes are happening
    command = "MP4Box -add recorded_videos/test_video{}.h264 recorded_videos/test_video{}.mp4".format(cur_video_num, cur_video_num)
    stream = os.popen(command)
    time.sleep(20)                  # enough time for video to convert before sending over..

    # Send email with recorded video
    video_filename_url = 'recorded_videos/test_video{}.mp4'.format(cur_video_num)
    send_email_with_video(recipient_email, video_filename_url)
    print("SENT EMAIL WITH VIDEO FILE ATTACHED")


def proximity_sensor():
    # Disable GPIO warnings
    GPIO.setwarnings(False)

    # need two positives before starting video
    firstPositive = False
    # need five negatives before stopping video
    numNegatives = 1
    prevIsNegative = False

    # is currently detecting intruder
    hasIntruder = False
    # max distance in cm before an intruder is detected 
    MAX_DETECTED_DIST = 100

    GPIO.setmode(GPIO.BCM)

    TRIG = 23 #always refers to real GPIO number
    ECHO = 24

    print("STATE: NOT RECORDING..")

    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    GPIO.output(TRIG, False)
    # waiting for sensor to settle
    time.sleep(2)

    while camIsEnabled:
        # take distance measurement every 3 seconds
        time.sleep(0.5)

        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150 #wavelength of wave emitted in cm
        distance = round(distance, 2) #round to 2 d.p or s.f?
        print("Distance: " + str(distance) + "cm")


        if distance < MAX_DETECTED_DIST:
            if prevIsNegative:
                prevIsNegative = False
                numNegatives = 1            # should start with 1 cos previsNegative takes 1 loop before incrementing
            if not firstPositive:
                firstPositive = True
            else:
                firstPositive = False
                # print("INTRUDER IS HERE!!!")
                # start video recording
                if not hasIntruder:
                    print("STATE: RECORDING..")
                    start_recording()
                    hasIntruder = True
        else:
            if firstPositive:
                firstPositive = False
            if hasIntruder:
                # print("INTRUDER HAS LEFT!!!")
                if numNegatives >= 5:
                    # stop video recording
                    print("STATE: NOT RECORDING..")
                    stop_recording()
                    hasIntruder = False
                    numNegatives = 1            # should start with 1 cos previsNegative takes 1 loop before incrementing
                    prevIsNegative = False
                else:
                    if prevIsNegative:
                        numNegatives += 1
                    else:
                        prevIsNegative = True


if __name__=='__main__':
    app.run()
