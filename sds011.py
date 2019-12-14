import serial
import logging
from .command import *


logging.getLogger(__name__)


class SDS011:

    def __init__(self, device_port):
        self.unit = "µg/m³"
        self._firmware = None
        self._device_id = None

        self.device = serial.Serial(
            port=device_port,
            baudrate=9600,
            stopbits=serial.STOPBITS_ONE,
            parity=serial.PARITY_NONE,
            bytesize=serial.EIGHTBITS,
            timeout=3
        )

    def _get_firmware_version(self):
        pass

    def _prepare_checksum(self, message: bytearray) -> int:
        checksum = 0
        for i in range(2, len(message)):
            checksum = checksum + message[i]

        return checksum % 256

    def _prepare_message(self, command: Command, data: bytearray) -> bytearray:
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

    def _send_request(self, command, data):
        message = self._prepare_message(command, data)

        # example message
        # aa: b4:02: 01:00: 00:00: 00:00: 00:00: 00:00: 00:00: ff:ff: 01:ab
