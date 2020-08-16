import RPi.GPIO as GPIO
import time

GPIO.setmode (GPIO.BCM)

GPIO.setup(16,GPIO.OUT)

while True:
    val=input()
    if val=="ON":
        GPIO.output(16,True)
    elif val=="OFF":
        GPIO.output(16,False)
        
GPIO.cleanup()


# # GPIO.setup(20,GPIO.OUT)
# # GPIO.setup(21,GPIO.OUT)
# 
# pwm=GPIO.PWM(16, 100)
# 
# while True:
#     pwm.start(10)
#     GPIO.output(21,True)
#     GPIO.output(20,False)
#     GPIO.output(16,True)
#     pwm.ChangeDutyCycle(100)
#     GPIO.output(21,True)
#     GPIO.output(20,False)
#     GPIO.output(16,True)
#     time.sleep(20)
#     GPIO.output(16,False)
#     
#     pwm.stop()
# GPIO.cleanup()
    
    