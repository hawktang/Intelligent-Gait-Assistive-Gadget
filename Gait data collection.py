import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import RPi.GPIO as GPIO
from Adafruit_ADS1x15 import ADS1115
from VL6180X import VL6180X
from MPU9250 import MPU9250

#Proximity initialization

tof_address = 0x29
tof_sensor = VL6180X(address=tof_address, debug=False) 
tof_sensor.default_settings()

##ADC initialization
adc_address_right = 0x48
adc_address_left = 0x49

adc = {}

adc['right'] = ADS1115(adc_address_right)
adc['left'] = ADS1115(adc_address_left)

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

##IMU initialization

imu_address_right = 0x68
imu_address_left = 0x69

imu = {}

imu['right'] = MPU9250(imu_address_right)
imu['left'] = MPU9250(imu_address_left)


#data collection

frame = 50
frame_length = 28
total_length = frame_length*frame

index = [np.repeat(np.arange(frame),frame_length),
         (['bilateral']*2+['left']*13+['right']*13)*frame,
         (['proximity','ambient']+(['adc']*4+['gyro']*3+['accelerometer']*3+['compass']*3)*2)*frame,
         (['distance','light']+(['0','1','2','3']+['x','y','z']*3)*2)*frame]

s = pd.Series(np.nan, index=index).sort_index()

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
        

s.to_csv('sensor.csv')




