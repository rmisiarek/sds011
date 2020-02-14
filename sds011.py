import datetime
import struct
from sys import exit
from typing import Optional, Union

import serial

from .packet import *
from .tests import *
from .utils import *

logging.basicConfig(format="%(asctime)s %(levelname)s:\t%(message)s", datefmt="%d-%b-%y %H:%M:%S", level=logging.INFO)
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

        if response:
            if response[BytePosition.Head] == Byte.Head:
                return response
            else:
                logging.error(f"SDS011: Invalid response")

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
        self.work_mode = None
        self.device_id = None
        self.duty_cycle = None
        self.firmware_version = None
        self.sender = None
        self.unit = "µg/m³"

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
            logging.error(f"SDS011: {e}")
        else:
            logging.info(f"SDS011: device on {device_port} - OK")
            self.sender = Sender(device=self.device)
            self.wake_sensor_up()
            sleep(1)
            self.get_config(print_config=True)

    def set_communication_mode(self, communication_mode: CommandValue):
        response = self.sender.communicate(set_communication_mode(communication_mode=communication_mode))
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

    @passive_mode
    def query(self):
        response = self.sender.communicate(query_data())
        if response:
            return self.extract_pm_values(data=response)
        return None

    @passive_mode
    def set_device_id(self, byte12: int, byte13: int):
        response = self.sender.communicate(set_device_id(byte12=byte12, byte13=byte13))
        if response:
            self.device_id = f"{response[BytePosition.Data5]:02d}{response[BytePosition.Data6]:02d}"
            return self.device_id
        return None

    @passive_mode
    def get_device_id(self):
        response = self.sender.communicate(get_device_id())
        if response:
            self.device_id = f"{response[BytePosition.Data5]:02d}{response[BytePosition.Data6]:02d}"
            return self.device_id
        return None

    @passive_mode
    def set_work_mode(self, work_mode: CommandValue):
        response = self.sender.communicate(set_work_mode(work_mode=work_mode))
        if response:
            self.work_mode = response[BytePosition.Data3]
            return self.work_mode
        return None

    @passive_mode
    def get_work_mode(self):
        response = self.sender.communicate(get_work_mode())
        if response:
            self.work_mode = response[BytePosition.Data3]
            return self.work_mode
        return None

    @active_mode
    def set_duty_cycle(self, period: int = 0):
        response = self.sender.communicate(set_duty_cycle(period=period))
        if response:
            self.duty_cycle = response[BytePosition.Data3]
            return self.duty_cycle
        return None

    @passive_mode
    def get_duty_cycle(self):
        response = self.sender.communicate(get_duty_cycle())
        if response:
            self.duty_cycle = response[BytePosition.Data3]
            return self.duty_cycle
        return None

    @passive_mode
    def get_firmware_version(self):
        response = self.sender.communicate(get_firmware_version())
        if response:
            self.firmware_version = f"{response[BytePosition.Data2]:02d}" \
                                    f"{response[BytePosition.Data3]:02d}" \
                                    f"{response[BytePosition.Data4]:02d}"
            return self.firmware_version
        return None

    @staticmethod
    def extract_pm_values(data):
        pm25 = 0
        pm10 = 0
        if data:
            pm25 = float(data[BytePosition.Data1] + data[BytePosition.Data2] * 256) / 10.0
            pm10 = float(data[BytePosition.Data3] + data[BytePosition.Data4] * 256) / 10.0

        values = {
            "pm25": pm25,
            "pm10": pm10,
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return values

    def get_config(self, print_config=False):
        logging.info("SDS011: Getting configuration from device ...")
        self.firmware_version = self.get_firmware_version()
        self.device_id = self.get_device_id()
        self.duty_cycle = self.get_duty_cycle()
        self.work_mode = self.get_work_mode()
        self.communication_mode = self.get_communication_mode()

        if print_config:
            print(f"=" * 45)
            print(f"\tFirmware:\t\t{self.firmware_version}")
            print(f"\tDevice ID:\t\t{self.device_id}")
            print(f"\tDuty cycle:\t\t{self.duty_cycle}")
            print(f"\tWork mode:\t\t{self.work_mode}")
            print(f"\tCommunication mode:\t{self.communication_mode}")
            print(f"=" * 45)

    def wake_sensor_up(self):
        self.sender.communicate(set_duty_cycle())
        self.sender.communicate(set_work_mode(CommandValue.Measuring))
        self.sender.communicate(set_communication_mode(CommandValue.Passive))


if __name__ == "__main__":
    sensor = SDS011("/dev/ttyUSB0")

    # run_all_tests(sensor)

    sensor.set_duty_cycle(1)
    while True:
        try:
            r = sensor.sender.read()
            if sensor.sender.is_valid_active_response(r):
                print(f"{sensor.extract_pm_values(r)}")
        except KeyboardInterrupt:
            exit("\nBye!")
