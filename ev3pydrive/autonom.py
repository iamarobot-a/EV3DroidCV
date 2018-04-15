#!/usr/bin/env python3

# This is a modified version of the code on
# https://github.com/rhempel/ev3dev-lang-python/blob/master/demo/auto-drive.py
# Normally you should stop the program by pressing any EV3 button
# but the line   btn=Button()    gave me an error so I commented it out
# and also changed the    while    line to    while True instead of referring
# to the buttons. This means the program can only be stopped with Ctrl-C


# -----------------------------------------------------------------------------
# Copyright (c) 2015 Denis Demidov <dennis.demidov@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# -----------------------------------------------------------------------------

# In this demo an Explor3r robot with touch sensor attachement drives
# autonomously. It drives forward until an obstacle is bumped (determined by
# the touch sensor), then turns in a random direction and continues. The robot
# slows down when it senses obstacle ahead (with the infrared sensor).
#
# The program may be stopped by pressing any button on the brick.
#
# This demonstrates usage of motors, sound, sensors, buttons, and leds.

from random import choice, randint
from ev3dev.ev3 import *
from tcpclient import Safestack,Director
from time import sleep, gmtime, strftime

Sound.set_volume(30)
# Connect two large motors on output ports B and C:
motors = [LargeMotor(address) for address in (OUTPUT_B, OUTPUT_C)]

# Every device in ev3dev has `connected` property. Use it to check that the
# device has actually been connected.
assert all([m.connected for m in motors]), \
    "Two large motors should be connected to ports B and C"

# Connect infrared and touch sensors.
ir = InfraredSensor()
#assert ir.connected
ts = TouchSensor()
#assert ts.connected("CONNECT Touch sensor!")
# Put the infrared sensor into proximity mode.
ir.mode = 'IR-PROX'

mL=LargeMotor('outB')
mR=LargeMotor('outC')
mH=MediumMotor('outA')
tooClose=50
stack=Safestack(10)
director=Director(stack,"192.168.45.133",1234)
# director.run()
# We will need to check EV3 buttons state.
# btn = Button()   NOT WORKING

def tsGetValue():
    return ts.value()
    #return  1==0


#FUNCTIONS
def headmover(grades,speed):
    # mH.run_to_abs_pos(position_sp=grades, speed_sp=speed)
    # mH.wait_until_not_moving(timeout=1000)
    # time.sleep(0.5)
    return ir.value()

def restart():
    """
    Start both motors. `run_forever` command will allow to vary motor
    performance on the fly by adjusting `speed_sp` attribute.
    """
    print("restart called")
    power = (1,1) #choice([(1, 1), (1, 1)])
    t = 250
    for m, p1 in zip(motors, power):
        m.run_timed(speed_sp=p1*200, time_sp=t)

    # Wait until both motors are stopped:
    while any(m.state for m in motors):
        sleep(0.1)

    for m in motors:
        m.run_forever()

def backup():
    """
    Back away from an obstacle.
    """
    print("backup called")
    # Sound backup alarm.
    Sound.tone([(1000, 500, 500)] * 3)

    # Turn backup lights on:
    for light in (Leds.LEFT, Leds.RIGHT):
        Leds.set_color(light, Leds.RED)

    # Stop both motors and reverse for 1.5 seconds.
    # `run-timed` command will return immediately, so we will have to wait
    # until both motors are stopped before continuing.
    for m in motors:
        m.stop(stop_action='brake')
        m.run_timed(speed_sp=-200, time_sp=1500)

    # When motor is stopped, its `state` attribute returns empty list.
    # Wait until both motors are stopped:
    while any(m.state for m in motors):
        sleep(0.1)

    # Turn backup lights off:
    for light in (Leds.LEFT, Leds.RIGHT):
        Leds.set_color(light, Leds.GREEN)

def turn():
    """
    Turn the robot in random direction.
    """

    # We want to turn the robot wheels in opposite directions from 1/4 to 3/4
    # of a second. Use `random.choice()` to decide which wheel will turn which
    # way.
    print("turn called")
    power = choice([(1, -1), (-1, 1)])
    t = randint(250, 750)

    for m, p in zip(motors, power):
        m.run_timed(speed_sp=p*200, time_sp=t)

    # Wait until both motors are stopped:
    while any(m.state for m in motors):
        sleep(0.1)
def turntoway(grades):
    print ("Turning to angle ", grades)
    turngrades = abs(grades*25) #2400 - 26.66
    sp1=250
    spL=-sp1
    spR=sp1
    if grades<0:
            spL=sp1
            spR=-sp1
    mL.wait_until_not_moving(timeout=1000)
    mR.wait_until_not_moving(timeout=1000)
    mL.run_timed(time_sp=turngrades, speed_sp=spL)
    mR.run_timed(time_sp=turngrades, speed_sp=spR)
    mL.wait_until_not_moving(timeout=1000)
    mR.wait_until_not_moving(timeout=1000)
    time.sleep(0.3)

def stop():
    print("Stopping...")
    for m in motors:
        m.stop()
Steps={}
Steps["BUMPED"]=[stop,backup,turn,restart]
Steps["AVOID"]=[stop,turntoway]
# Run the robot until a button is pressed.
#ENTRY POINT
try:
    dc=50
    ldc=0
    ldist=100
    for m in motors:
         m.speed_sp=200
    headmover(0,100)
    # start()
    print("Program started.")
    State="FORWARD"
    NewState=""
    StateCtr=0
    StateChgCtr=0
    # while not btn.any():   NOT WORKING
    while True:    # Stop program with Ctrl-C
        NewState=""
        distance = ir.value()
        StateCtr=StateCtr+1
        if distance<tooClose:
            #will be changed to a more proper path finding
            print ("Object too close:%" ,distance )
            NewState="AVOID"
        if tsGetValue():
            NewState="BUMPED"
        print("State, NewState:",State,NewState)
        if NewState=="":
            cameradir=stack.pop()
            if (cameradir!=""):
                w=cameradir[:1]
                if w in ["R","L","B","F"]:
                    NewState="FOLLOW"
                if w in ["X","Y","Z"]:
                    NewState="AVOIDCAM"

        if NewState!="" and NewState!=State:
            print ("State changing from %s to %s",State,NewState)
            State=NewState
            StateChgCtr=StateCtr
        if State=="BUMPED":
            ctr=StateCtr-StateChgCtr
            steps=Steps["BUMPED"]
            if ctr>=len(steps):
                State="FORWARD"
                continue
            else:
                step=steps[ctr]
                print ("step for bump:",step)
                step()
        if State=="FORWARD":
            # print ("running:",mL.is_running,mR.is_running)
            if mL.is_running==False:
                print ("start L")
                mL.run_forever()
            if mR.is_running==False:
                print ("start R")
                mR.run_forever()
        if State=="AVOID":
            ctr=StateCtr-StateChgCtr
            steps=Steps["AVOID"]
            if ctr>=len(steps):
                ctr=1
            step=steps[ctr]
            print ("step for avoid:",step)
            if ctr==0:
                stop()
            else:
                angle=30
                turntoway(angle)
                if ir.value()>tooClose:
                    print("found a way.")
                    restart()
                    State="FORWARD"
                    continue
        sleep(0.1)

except KeyboardInterrupt:
    print("W: interrupt received")
finally:
    # clean up
    director.close()
    stop()
    headmover(0, 100)
