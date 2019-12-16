import logging
import struct
from time import sleep

import serial

from command import *

logging.basicConfig(
    format="%(asctime)s : %(levelname)s\t%(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.DEBUG
)
logging.getLogger(__name__)


class SDS011:

    def __init__(self, device_port):
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
            # self._load_config()
            # sleep(5)
            # self._set_measuring_state()
            # sleep(5)
            # self._set_sleeping_state()
            # sleep(5)
            # self._set_measuring_state()

    def _load_config(self):
        logging.info(f"SDS011: loading config data...")
        self._get_firmware_version()
        self._get_device_id()
        logging.info(f"SDS011: loading config data - OK")

    @property
    def firmware(self):
        return self._firmware

    @property
    def work_mode(self):
        return self._work_mode

    @work_mode.setter
    def work_mode(self, value):
        if isinstance(value, WorkMode):
            response = self._send_request(
                command=Command.WorkMode,
                data=self._prepare_data(CommandMode.Set, value))
            if response and response[BytePosition.Data1] == value:
                self._work_mode = value
        else:
            raise TypeError(f"WorkMode have to be type of {WorkMode.Measuring=} or {WorkMode.Sleeping=}")

    def print_config(self):
        print(f"=" * 40)
        print(f"\tFirmware:\t{self.firmware}")
        print(f"\tDevice ID:\t{self._device_id}")
        print(f"=" * 40)

    def _get_firmware_version(self):
        response = self._send_request(
            command=Command.Firmware,
            data=self._prepare_data(CommandMode.Get, 0)
        )
        if response and response[BytePosition.Data1] == Command.Firmware:
            self._firmware = "{0:02d}{1:02d}{2:02d}".format(response[3], response[4], response[5])

    def _get_device_id(self):
        response = self._send_request(
            command=Command.DeviceId,
            data=self._prepare_data(CommandMode.Get, 0)
        )
        if response and response[BytePosition.Data1] == Command.DeviceId:
            self._device_id = "{0:02d}{1:02d}".format(response[BytePosition.Data5], response[BytePosition.Data6])

    def _set_measuring_state(self):
        response = self._send_request(
            command=Command.WorkMode,
            data=self._prepare_data(CommandMode.Set, WorkMode.Measuring))
        if response and response[BytePosition.Data1] == Command.WorkMode:
            self._work_mode = WorkMode.Measuring

    def _set_sleeping_state(self):
        response = self._send_request(
            command=Command.WorkMode,
            data=self._prepare_data(CommandMode.Set, WorkMode.Sleeping))
        if response and response[BytePosition.Data1] == Command.WorkMode:
            self._work_mode = WorkMode.Sleeping

    @staticmethod
    def _prepare_checksum(message: bytearray) -> int:
        checksum = 0
        for i in range(2, len(message)):
            checksum = checksum + message[i]

        return checksum % 256

    def _prepare_command(self, command: Command, data: bytearray) -> bytearray:
        message = bytearray()
        message.append(Byte.Head.value)
        message.append(Byte.CommandID.value)
        message.append(command.value)
        for i in range(0, 12):
            if i < len(data):
                message.append(data[i])
            else:
                message.append(0)
        message.append(Byte.CommandEnd.value)
        message.append(Byte.CommandEnd.value)
        checksum = self._prepare_checksum(message=message)
        message.append(checksum)
        message.append(Byte.Tail.value)
        return message

    @staticmethod
    def _prepare_data(command_mode: CommandMode, command_value: int) -> bytearray:
        data = bytearray()
        data.append(command_mode)
        data.append(command_value)
        return data

    def _validate_written_data(self, written_bytes, _len: int) -> (bool, int):
        self.device.flush()
        if written_bytes != Length.Command.value:
            raise IOError(f"SDS011: sent {written_bytes} bytes, expected {Length.Command.value} bytes")

    def _send_request(self, command: Command, data: bytearray) -> tuple:
        message_bytes = self._prepare_command(command, data)
        logging.info(f"SDS011: sending message {message_bytes}")
        written_bytes = self.device.write(message_bytes)
        self._validate_written_data(written_bytes=written_bytes, _len=len(message_bytes))
        response = self._process_response()
        return response

    def _process_response(self):

        def valid_passiv_response(_bytes: bytes) -> bool:
            return (_bytes[0] == Byte.Head) and (_bytes[1] == Byte.PassivResponse)

        def valid_initiative_response(_bytes: bytes) -> bool:
            return (_bytes[0] == Byte.Head) and (_bytes[1] == Byte.InitiativeResponse)

        while True:
            received_bytes = self.device.read(Length.Response)
            if len(received_bytes) != Length.Response.value:
                raise IOError(f"SDS011: received {len(received_bytes)} bytes, expected {Length.Response.value} bytes")

            checksum = self._prepare_checksum(received_bytes[0:-2])
            if checksum != received_bytes[-2]:
                raise IOError(f"SDS011: {checksum=} is invalid")

            if not valid_passiv_response(_bytes=received_bytes[0:2]):
                break
            else:
                logging.debug(f"[ PassivResponse ] {received_bytes=}, {struct.unpack('BBBBBBBBBB', received_bytes)=}")
                # logging.info(f"SDS011: got response [ P ]: {received_bytes}")

            if not valid_initiative_response(_bytes=received_bytes[0:2]):
                break
            else:
                logging.debug(f"[ InitiativeResponse ] {received_bytes=}, {struct.unpack('BBBBBBBBBB', received_bytes)}")
                # logging.info(f"SDS011: got response [ I ]: {received_bytes}")

        return struct.unpack('BBBBBBBBBB', received_bytes)


if __name__ == "__main__":
    sensor = SDS011("/dev/ttyUSB0")
    sensor.print_config()
    sleep(5)
    sensor.work_mode = WorkMode.Sleeping
    sleep(5)
    sensor.work_mode = WorkMode.Measuring
    sleep(5)

        # example message
        # aa: b4:02: 01:00: 00:00: 00:00: 00:00: 00:00: 00:00: ff:ff: 01:ab
