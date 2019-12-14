import serial
import struct
from datetime import datetime


PORT = "/dev/ttyUSB0"   # linux
UNPACK_PAT = "<ccHHHcc"

with serial.Serial(PORT, 9600, bytesize=8, parity="N", stopbits=1) as ser:
    while True:
        data = ser.read(10)
        unpacked = struct.unpack(UNPACK_PAT, data)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pm25 = unpacked[2] / 10.0
        pm10 = unpacked[3] / 10.0
        print(f"[ {ts} ]: PM 2.5 = {pm25}, PM10 = {pm10}")
