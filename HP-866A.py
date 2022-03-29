#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  7 23:11:14 2022

@author: Borisov
"""

# Support Hold Peak HP-866A Digital Anemometer

import serial
import time

class HP866A:
    def __init__(self, port, log_file):
        self.device = serial.Serial(port)
        self.device.timeout = 2
        print(self.device)
        self.cnt = 0
        self.packet = bytes()
        self.log = open(log_file, 'w')
        self.log.write('time,humidity,temperature,func,measurement,unit\n')
        self.start_log = 1
        
    def close(self):
        self.device.close()
        self.log.close()
        
    def read_packet(self):
        self.cnt = 0
        while self.start_log == 1:
            byte = self.device.read(1)
     
            if self.cnt == 0:
                if byte == b'\xeb':
                    self.cnt = self.cnt + 1
            elif self.cnt == 1:
                if byte == b'\xa0':
                    self.cnt = self.cnt + 1
                    self.packet = b''
                else:
                    self.cnt = 0
            elif 1 < self.cnt < 15:
                self.packet = self.packet + byte
                self.cnt = self.cnt + 1
            elif self.cnt == 15:
                if byte == b'\x11':
                    # print('received {}'.format(self.packet))
                    self.decode_packet()
                self.cnt = 0
                
    def decode_packet(self):
        unit = 0
        func = 0
        if self.packet[0]  == 0 or self.packet[0]  == 8:
            func = 'VEL'
            if self.packet[1]  == 0:
                unit = 'm/s'
            elif self.packet[1]  == 4:
                unit = 'km/h'
            if self.packet[1]  == 8:
                unit = 'MPH'
            elif self.packet[1]  == 12:
                unit = 'ft/m'
            elif self.packet[1]  == 16:
                unit = 'ft/s'
            elif self.packet[1]  == 20:
                unit = 'knots'                
        elif self.packet[0]  == 1:
            func = 'AREA'
        elif self.packet[0]  == 2:
            func = 'FLOW'
            if self.packet[1]  == 0:
                unit = 'CMM'
            elif self.packet[1]  == 4:
                unit = 'CMS'
            if self.packet[1]  == 8:
                unit = 'CFM'         
        elif self.packet[0] == 32:
            func = 'DP'
        elif self.packet[0] == 64:
            func = 'WB'
        
        humidity = float(int.from_bytes(self.packet[2:4], byteorder='big', signed='false')) / 10
        temperature = float(int.from_bytes(self.packet[4:6], byteorder='big', signed='false')) / 10 - 30
        measurement = float(int.from_bytes(self.packet[6:8], byteorder='big', signed='false')) / 100
        print('{} %, {:.1f} C {} {} {}'.format(humidity, temperature, func, measurement, unit))
        print(func, unit, self.packet[0], self.packet[1])
        self.log.write('{},{:.1f},{:.1f},{},{:.1f},{}\n'.format(time.strftime('%d.%m.%Y %H:%M:%S'),humidity, temperature, func, measurement, unit))
        self.log.flush()
        
        
            
#    def decode(self, byte):         
        
if __name__ == '__main__':
    log_file = './log/anemometer_' + time.strftime('%Y_%m_%d_%H:%M:%S') + '.csv'
    anemometer = HP866A('/dev/ttyUSB1', log_file)
    anemometer.read_packet()

    anemometer.close()