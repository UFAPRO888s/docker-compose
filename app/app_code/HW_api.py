#!/usr/bin/python3
import _thread
import time
import smbus
from HW_lib.PCA9685 import PCA9685 as PWM
from HW_lib.ServoPCA9685 import ServoPCA9685 as Servo
from HW_lib.MPU6050 import MPU6050 as IMU
from HW_lib.TCA9548A import TCA9548A as i2cHub
from HW_lib.AS5600 import AS5600 as Encoder
import numpy as np
import signal
import time
import cv2
import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException, File,Form, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, FileResponse,StreamingResponse
from pydantic import BaseModel
import json
import jinja2
import base64
import io
# import collections
import math
from typing import Union
from dataclasses import dataclass
# from PIL import Image

run = True
i2cBus = smbus.SMBus(0)
i2cBus0 = i2cHub(bus=i2cBus, channel=0)
i2cBus1 = i2cHub(bus=i2cBus, channel=1)
i2cBus2 = i2cHub(bus=i2cBus, channel=2)
i2cBus3 = i2cHub(bus=i2cBus, channel=3)
# i2cBus4 = i2cHub(bus=i2cBus, channel=4)
# i2cBus5 = i2cHub(bus=i2cBus, channel=5)
# i2cBus6 = i2cHub(bus=i2cBus, channel=6)
# i2cBus7 = i2cHub(bus=i2cBus, channel=7)

pwm_gen = PWM(i2cBus0)
imu_sensor = IMU(i2cBus1)
encoder1 = Encoder(i2cBus2)
encoder2 = Encoder(i2cBus3)
servo00 = Servo(pwm_gen, pwm_gen.CHANNEL00)
servo01 = Servo(pwm_gen, pwm_gen.CHANNEL01)
enable_cam=False
if enable_cam:
    camera = cv2.VideoCapture(1)

@dataclass
class Pose():
    position:float
    velocity:float
    acceleration:float
    
@dataclass
class Cartitians():
    x:float
    y:float
    z:float
    
@dataclass
class Time():
    now:float
    prev:float
    Ts:float
    def update(self):
        self.prev = self.now
        self.now = time.perf_counter()
        if (self.prev==self.prev) and (self.now==self.now): ## equality test for nan
            self.Ts = self.now-self.prev
        else:
            self.Ts = float('nan')

class PID():
    time=Time(float('nan'),float('nan'),float('nan'))
    e_now=0.0
    e_prev=0.0
    kP=0.0
    kI=0.0
    kD=0.0
    Integral=0.0
    Derivative=0.0
    out=0.0
    target=0.0
    current=0.0
    def set_gain(self,kP, kI, kD):
        self.kP=kP
        self.kI=kI
        self.kD=kD
    def update(self,target,current):
        if math.isnan(target)|math.isnan(current): return 0
        self.time.update()
        self.e_prev = 0.0 if math.isnan(self.e_now) else self.e_now
        self.e_now = target-current
        if self.time.Ts > 0.0:
            self.Integral = self.Integral + (self.e_now*self.time.Ts)
            self.Derivative = (self.e_now - self.e_prev)/self.time.Ts
            self.Integral=np.clip(float(self.Integral), -1.0, 1.0)
            self.Derivative=np.clip(float(self.Derivative), -1.0, 1.0)
            self.out = (self.kP*self.e_now) + (self.kI*self.Integral) + (self.kD*self.Derivative)
            self.out = np.clip(self.out, -1.0, 1.0)
        else:
            self.out = 0.0
        return self.out
    def __get__(self):
        return self.update(self.target,self.current)
    def __set__(self,current,target):
        self.current =current
        self.target =target
        

class Sensors():
    time=Time(float('nan'),float('nan'),float('nan'))
    accel=Cartitians(0,0,0)
    gyro=Cartitians(0,0,0)
    wheel1=Pose(0,0,0)
    wheel2=Pose(0,0,0)
    wheel1_prev=Pose(0,0,0)
    wheel2_prev=Pose(0,0,0)
    def update(self):
        self.time.update()
        Ts=self.time.Ts
        self.wheel1_prev=self.wheel1
        self.wheel2_prev=self.wheel2
        self.accel.x,self.accel.y,self.accel.z=imu_sensor.get_accelerometer()
        self.gyro.x,self.gyro.y,self.gyro.z=imu_sensor.get_gyroscope()
        self.wheel1.position=-encoder1.get_position()
        self.wheel2.position=encoder2.get_position()
        if Ts==Ts:
            self.wheel1.velocity=(self.wheel1.position-self.wheel1_prev.position)/Ts
            self.wheel2.velocity=(self.wheel2.position-self.wheel2_prev.position)/Ts
            self.wheel1.acceleration=(self.wheel1.velocity-self.wheel1_prev.velocity)/Ts
            self.wheel2.acceleration=(self.wheel2.velocity-self.wheel2_prev.velocity)/Ts

class quintic_coefficients():
    v_max=1.0
    a_max=1.0
    T_i=time.perf_counter()
    T_f=T_i
    Coeff=np.zeros(6)
    def calculate(self,initial,final):
        D=final-initial
        if D!=0:
            Tk=max([(15*np.abs(D))/(8*self.v_max),np.sqrt(10*np.abs(D)/(np.sqrt(3)*self.a_max))]);
            print("D:",D,"Tk:",Tk)
            c0=initial
            c1=0
            c2=0
            c3=10*D/(Tk**3)
            c4=-15*D/(Tk**4)
            c5=6*D/(Tk**5)
            self.Coeff=np.array([c0,c1,c2,c3,c4,c5],dtype=np.float)
            self.T_i=time.perf_counter()
            self.T_f=self.T_i+Tk
        else:
            self.Coeff=np.zeros(6)
        print(self.Coeff)

class quintic_trajectory():
    props=quintic_coefficients()
    pose=Pose(0,0,0)
    def __init__(self):
        self.pose.position=0
        self.pose.velocity=0
        self.pose.acceleration=0
    def eval(self):
        t_now=time.perf_counter()
        if t_now>=self.props.T_i and t_now<=self.props.T_f:
            tau1=time.perf_counter()-self.props.T_i
            tau2=tau1**2
            tau3=tau1**3
            tau4=tau1**4
            tau5=tau1**5
            pp=np.dot(self.props.Coeff,np.array([[1,tau1,tau2,tau3,tau4,tau5],[0,1,2*tau1,3*tau2,4*tau3,5*tau4],[0,0,2,6*tau1,12*tau2,20*tau3]]).transpose())
            print(pp)
            self.pose.position=pp[0]
            self.pose.velocity=pp[1]
            self.pose.acceleration=pp[2]
        else:
            if math.isnan(self.pose.position):
                self.pose.position=0
            self.pose.velocity=0
            self.pose.acceleration=0
        # print(self.pose)
        # print("eval",self.props.Coeff)
        return self.pose

    def calculate(self,initial,final):
        self.props.calculate(initial,final)

class Trajecteries():
    time=Time(0,0,0)
    wheel1=Pose(0,0,0)
    wheel2=Pose(0,0,0)
    planner1=quintic_trajectory()
    planner2=quintic_trajectory()
    def update(self):
        self.time.update()
        self.wheel1=self.planner1.eval()
        self.wheel2=self.planner2.eval()
    def set_target1(self, target1):
        self.planner1.calculate(sensors.wheel1.position, target1)
    def set_target2(self, target2):
        self.planner2.calculate(sensors.wheel2.position, target2)


app = FastAPI(openapi_url=None)
app.mount('/imgstore', StaticFiles(directory='./imgstore'), name='imgstore')
app.mount('/static', StaticFiles(directory='./server/static'), name='static')

templates = Jinja2Templates(directory='./server')
templates.env.globals["urlpath"] = app.url_path_for
templates.env.trim_blocks = True
templates.env.lstrip_blocks = True
templates.env.autoescape = False

templates.env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')

def hw_ctl(traj,sensors,pid1,pid2):
    # global run,traj
    while True:
        # try:
        sensors.update()
        # print(traj.wheel1.position)
        # print(traj.wheel2.position)
        # print("input:",sensors.wheel1.position,traj.wheel1.position)
        out1=pid1.update(current=sensors.wheel1.position,target=traj.wheel1.position)
        out2=pid2.update(current=sensors.wheel2.position,target=traj.wheel2.position)
        # print("output:",out1,out2)
        servo00.set_percent(out1)
        servo01.set_percent(out2)
        # except Exception as e:
        #     print(e)
        #     pass
        time.sleep(0.001)
    end_prog()

def trajectory_generator(traj,sensors,pid1,pid2):
    # global run,traj
    while True:
        traj.update()
        time.sleep(0.1)

def monitor(traj,sensors,pid1,pid2):
    while True:
        m=[# sensors.accel.x,
                # sensors.accel.y,
                # sensors.accel.z,
                # sensors.gyro.x,
                # sensors.gyro.y,
                # sensors.gyro.z,
                sensors.wheel1.position,
                sensors.wheel1.velocity,
                sensors.wheel1.acceleration,
                sensors.wheel2.position,
                sensors.wheel2.velocity,
                sensors.wheel2.acceleration,]
        s=", ".join(["{:.2f}".format(i) for i in m])
        print(s)
        time.sleep(0.2)

def end_prog():
    print("exiting...")
    servo00.disable()
    servo01.disable() 
    time.sleep(0.1)   
    i2cBus.close()
    time.sleep(0.1) 
    exit(0)
    
def handler(signum, frame):
    global run
    try:
        res = input('Ctrl-c was pressed. Do you really want to exit? y/n ')
        if res.lower() == 'y':
            run = False
    except:
        end_prog()
        
@app.get('/')
async def index(request: Request):
	return templates.TemplateResponse('api.pug', {'request': request,})
@app.get('/goto')
async def goto(motor1: Union[float, None], motor2:Union[float, None]):
    if motor1 is not None:
        traj.set_target1(motor1)
    if motor2 is not None:
        traj.set_target2(motor2)
    return "ok"
if enable_cam:
    @app.get('/capture')
    async def capture(type: str,res:Union[float, int]):
        _, image = camera.read()
        if res>1 and isinstance(res, int):
            image=image[::res,::res,:]
        elif res>0:
            width = int(image.shape[1] /res)
            height = int(image.shape[0] /res)
            dim = (width, height)
            # resize image
            image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
        _, image = cv2.imencode("."+type, image)
        return StreamingResponse(
        io.BytesIO(image),
        media_type='image/'+type)

@app.on_event("shutdown")
def shutdown_event():
    global run,camera
    run = False
    if enable_cam:
        camera.release
    time.sleep(0.5)
    with open("log.txt", mode="a") as log:
        log.write("Application shutdown\n")
        
@app.on_event("startup")
async def startup_event():
    with open("log.txt", mode="a") as log:
        log.write("Application start\n")

traj = Trajecteries()
sensors = Sensors()
pid1 = PID()
pid2 = PID()
pid1.set_gain(
    kP=0.01,
    kI=0.0,
    kD=0.001
    )
pid2.set_gain(
    kP=0.01,
    kI=0.0,
    kD=0.001
    )
if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    try:
        _thread.start_new_thread( hw_ctl, (traj,sensors,pid1,pid2) )
        # _thread.start_new_thread( monitor, (traj,sensors,pid1,pid2) )
        _thread.start_new_thread( trajectory_generator, (traj,sensors,pid1,pid2) )
    except:
        print ("Error: unable to start thread")
    uvicorn.run(app, host='', port=4000)
    



