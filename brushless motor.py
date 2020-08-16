import RPi.GPIO as GPIO
from time import sleep
 
GPIO.setmode (GPIO.BCM)
GPIO.setup(16,GPIO.OUT)

motor1=13 #pin in motor 1
motor2=12 #pin in motor 2


GPIO.setup(motor1,GPIO.OUT)
pwm1= GPIO.PWM(motor1,1000)
pwm1.start(0)



GPIO.setup(motor2,GPIO.OUT)
pwm2= GPIO.PWM(motor2,1000)
pwm2.start(0)

for i in range(0,100):
    print(i)
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

while True:
    val=input()
    if val=="W":
        maju1() #Untuk MAJU motor 1
        maju2() #Untuk MAJU motor 2
    elif val=="A":
        stop2() #Untuk STOP motor 2
        maju1() #Untuk MAJU motor 1
    elif val=="D":
        maju2() #Untuk MAJU motor 2
        stop1() #Untuk STOP motor 1  
    elif val=="S":
        stop1() #Untuk STOP motor 1
        stop2() #Untuk STOP motor 2
         
    elif val=="ON":       #Untuk Hidup Conveyor
        GPIO.output(16,True)
        print ("Conveyor ON")
    elif val=="OFF":      #Untuk Hidup Conveyor
        GPIO.output(16,False)
        print ("Conveyor OFF")
        

pwm1.stop()
pwm2.stop()

GPIO.cleanup()

# stop2() #Untuk STOP motor 2
# maju2() #Untuk MAJU motor 2


