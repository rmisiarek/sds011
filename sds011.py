import logging
import struct
from time import sleep
from typing import Optional, Union

import serial

from packet import *
from tests import *


logging.basicConfig(
    format="%(asctime)s : %(levelname)s\t%(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.DEBUG
)
logging.getLogger(__name__)


class Sender:

    def __init__(self, device):
        self.device = device

    def communicate(self, packet: Packet) -> Optional[tuple]:
        if not isinstance(packet.data1, Command):
            raise TypeError(f"CommandMode have to be type of {Command}")

        if not isinstance(packet.data2, CommandMode):
            raise TypeError(f"CommandValue have to be type of {CommandMode}")

        response = self.write(message=packet.message)

        if response and response[BytePosition.Data1] == packet.data1 and \
                response[BytePosition.Data2] == packet.data2:
            return response

        return None

    def write(self, message: bytearray) -> tuple:
        self.device.flush()
        logging.debug(f"device.write(): {message}")
        sent_bytes = self.device.write(message)
        if sent_bytes != Length.Command.value:
            raise IOError(f"SDS011: sent {sent_bytes} bytes, expected {Length.Command} bytes")

        return self.read()

    def read(self) -> tuple:
        self.device.flush()
        received_bytes = self.device.read(Length.Response)
        if received_bytes:
            logging.debug(f"device.read(): {received_bytes}")
            if len(received_bytes) != Length.Response:
                raise IOError(f"SDS011: received {len(received_bytes)} bytes, expected {Length.Response} bytes")

            return struct.unpack('BBBBBBBBBB', received_bytes)

    @staticmethod
    def is_valid_passive_response(response: Union[bytearray, tuple]) -> bool:
        if response:
            return (response[BytePosition.Head] == Byte.Head) and \
                   (response[BytePosition.CommandID] == Byte.PassiveResponse)

    @staticmethod
    def is_valid_active_response(response: Union[bytearray, tuple]) -> bool:
        if response:
            return (response[BytePosition.Head] == Byte.Head) and \
                   (response[BytePosition.CommandID] == Byte.ActiveResponse)


class SDS011:
    def __init__(self, device_port):
        self.communication_mode = None

        self.response = None
        self.sender = None
        self._unit = "µg/m³"
        self._firmware = None
        self._device_id = None
        self._work_mode = None

        try:
            self.device = serial.Serial(
                port=device_port,
                baudrate=9600,
                stopbits=serial.STOPBITS_ONE,
                parity=serial.PARITY_NONE,
                bytesize=serial.EIGHTBITS,
                timeout=3
            )
        except serial.SerialException as e:
            logging.error(e)
            raise
        else:
            logging.info(f"SDS011: device on {device_port} - OK")
            self.sender = Sender(device=self.device)
            # self.get_config(print_config=True)

    def set_communication_mode(self, communication_mode):
        response = self.sender.communicate(set_communication_mode_packet(communication_mode=communication_mode))
        if response:
            self.communication_mode = response[BytePosition.Data3]
            return self.communication_mode
        return None

    def get_communication_mode(self):
        response = self.sender.communicate(get_communication_mode())
        if response:
            self.communication_mode = response[BytePosition.Data3]
            return self.communication_mode
        return None

    def get_config(self, print_config=False):
        self.wake_sensor_up()
        self._firmware = self.firmware_version()
        self._device_id = self.device_id()
        self._work_mode = self.work_mode()
        self._communication_mode = self.communication_mode()

        if print_config:
            print(f"=" * 45)
            print(f"\tFirmware:\t\t{self._firmware}")
            print(f"\tDevice ID:\t\t{self._device_id}")
            print(f"\tWork mode:\t\t{self._work_mode}")
            print(f"\tCommunication mode:\t{self._communication_mode}")
            print(f"=" * 45)

    def wake_sensor_up(self):
        self.sender.communicate(work_mode_measuring())
        self.sender.communicate(get_duty_cycle_packet())

    def firmware_version(self):
        response = self.sender.communicate(get_firmware_version())
        if response:
            print('r: ', response)
            self.response = response
            return "{0:02d}{1:02d}{2:02d}".format(response[3], response[4], response[5])
        return None

    def device_id(self):
        response = self.sender.communicate(get_device_id())
        if response:
            self.response = response
            # return "{0:02d}{1:02d}".format(response[BytePosition.Data5], response[BytePosition.Data6])
        return None

    def work_mode(self):
        response = self.sender.communicate(get_work_mode())
        if response:
            self.response = response
            # return "{0:02d}{1:02d}".format(response[BytePosition.Data5], response[BytePosition.Data6])
        return None

    def duty_cycle(self):
        response = self.sender.communicate(get_duty_cycle_packet())
        if response:
            self.response = response
            # print(f"\t\tduty_cycle = {response}")
        return None

    def set_duty_cycle_period(self, period: int = 0):
        response = self.sender.communicate(set_duty_cycle_packet(period=period))
        if response:
            self.response = response
            # print(f"set_duty_cycle response {response}")
        return None


if __name__ == "__main__":
    sensor = SDS011("/dev/ttyUSB0")
    # sensor.set_duty_cycle_period(1)
    # while True:
    #     r = sensor.sender.read()
    #     if sensor.sender.is_valid_active_response(r):
    #         print(f'pomiar: {r}')

    test_communication_mode(sensor)

    # sensor.set_communication_mode(CommandValue.Active)
    # print(sensor.communication_mode())
