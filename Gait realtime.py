#sudo apt-get install python3 python3-pyqt5
#import matplotlib as matplotlib
#matplotlib.use('Qt5Agg')
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
from Adafruit_ADS1x15 import ADS1115
from VL6180X import VL6180X
from MPU9250 import MPU9250
from matplotlib.animation import FuncAnimation
from time import sleep
#Proximity initialization

try:
    tof_address = 0x29
    tof_sensor = VL6180X(address=tof_address, debug=False) 
    tof_sensor.default_settings()
except OSError:
    print("prximity connection error")


##ADC initialization

# Choose a gain of 1 for reading voltages from 0 to 4.09V.
# Or pick a different gain to change the range of voltages that are read:
#  - 2/3 = +/-6.144V
#  -   1 = +/-4.096V
#  -   2 = +/-2.048V
#  -   4 = +/-1.024V
#  -   8 = +/-0.512V
#  -  16 = +/-0.256V
# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.

GAIN = 1

adc_address_right = 0x48
adc_address_left = 0x49

adc = {}

adc['right'] = ADS1115(adc_address_right)
adc['left'] = ADS1115(adc_address_left)
    
##IMU initialization

imu_address_right = 0x68
imu_address_left = 0x69

imu = {}
try:
    imu['right'] = MPU9250(imu_address_right)
    imu['left'] = MPU9250(imu_address_left)
except OSError:
    print("imu connection error")

#data collection


frame = 1000
frame_length = 28
total_length = frame_length*frame

index = [np.repeat(np.arange(frame),frame_length),
         (['bilateral']*2+['left']*13+['right']*13)*frame,
         (['proximity','ambient']+(['adc']*4+['gyro']*3+['accelerometer']*3+['compass']*3)*2)*frame,
         (['distance','light']+(['0','1','2','3']+['x','y','z']*3)*2)*frame]

s = pd.Series(np.nan, index=index).sort_index()

'''

for i in range(frame):
    s[i,'bilateral','proximity','distance'] = tof_sensor.get_distance()
    s[i,'bilateral','ambient','light'] = tof_sensor.get_ambient_light(20) 
    for lateral in ['right','left']:
        for d in ['x','y','z']:
            s[i,lateral,'accelerometer',d] = imu[lateral].readAccel()[d]
            s[i,lateral,'gyro',d] = imu[lateral].readGyro()[d]
            s[i,lateral,'compass',d] = imu[lateral].readMagnet()[d]
        for ch in ['0','1','2','3']:        
            s[i,lateral,'adc',ch]= adc[lateral].read_adc(int(ch), gain=GAIN)

'''




fig, axis = plt.subplots(3,1)
fig.tight_layout() 

axis =pd.Series(axis,index=['1','2','3'])
curve ={
    '0':np.nan,
    '1':np.nan,
    '2':np.nan,
    '3':np.nan,
    '4':np.nan}

curve['0'], =axis['1'].plot([], [], lw=2)
curve['1'], =axis['2'].plot([], [], lw=2)
curve['2'], =axis['2'].plot([], [], lw=2,color='r')
curve['3'], =axis['3'].plot([], [], lw=2)
curve['4'], =axis['3'].plot([], [], lw=2,color='r')

for p in axis:
    p.set_xlim(0, frame)
    p.grid()
axis['1'].set_title("Proximity")
axis['1'].set_ylim(0,150)

axis['2'].set_title("Accelerometer")
axis['2'].set_ylim(-1,1)

axis['3'].set_title("ADC")
axis['3'].set_ylim(0,200)



def update(i):
    s[i,'bilateral','proximity','distance'] = tof_sensor.get_distance()
    #s[i,'bilateral','ambient','light'] = tof_sensor.get_ambient_light(20) 
    try:
        for lateral in ['right','left']:
            for d in ['z']: #for d in ['x','y','z']:
                s[i,lateral,'accelerometer',d] = imu[lateral].readAccel()[d]
                #s[i,lateral,'gyro',d] = imu[lateral].readGyro()[d]
                #s[i,lateral,'compass',d] = imu[lateral].readMagnet()[d]
            for ch in ['3']: # for ch in ['0','1','2','3']:       
                s[i,lateral,'adc',ch]= adc[lateral].read_adc(int(ch), gain=GAIN)
    except:
        sys.exit("connection error")

    curve['0'].set_data(range(frame),s[:,'bilateral','proximity','distance'])
    curve['1'].set_data(range(frame),s[:,'right','accelerometer','z'])
    curve['2'].set_data(range(frame),s[:,'left','accelerometer','z'])
    curve['3'].set_data(range(frame),s[:,'right','adc','3'])
    curve['4'].set_data(range(frame),s[:,'left','adc','3'])

    return curve.values()

ani = FuncAnimation(fig, update, range(frame), blit=True, interval=10, repeat=False)
plt.show()
