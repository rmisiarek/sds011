import logging

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
        else:
            logging.info(f"\nSDS011: device on {device_port} - OK")

    # def _get_firmware_version(self):
        # response = self._send_request(
        #     command=Command.Firmware,
        #     data=self._prepare_data(CommandMode.Get, 0)
        # )

    def _prepare_checksum(self, message: bytearray) -> int:
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
        logging.debug(f"{checksum=}")
        message.append(checksum)
        message.append(Byte.Tail.value)
        return message

    def _prepare_data(self, command_mode: CommandMode, command_value) -> bytearray:
        data = bytearray()
        data.append(command_mode)
        data.append(command_value)
        return data

    def _validate_written_data(self, written_bytes, _len: int) -> (bool, int):
        self.device.flush()
        if written_bytes != Length.Command.value:
            raise IOError(f"SDS011: sent {written_bytes} bytes, expected {Length.Command.value} bytes")

    def _send_request(self, command: Command, data: bytearray) -> bytearray:
        message_bytes = self._prepare_command(command, data)
        logging.info(f"SDS011: sending message {message_bytes}")
        written_bytes = self.device.write(message_bytes)
        self._validate_written_data(written_bytes=written_bytes, _len=len(message_bytes))

        response = self._process_response()

        return response

    def _process_response(self) -> bytearray:
        return bytearray()


if __name__ == "__main__":
    sensor = SDS011("/dev/ttyUSB0")
    sensor._send_request(Command.Query, bytearray(170))

        # example message
        # aa: b4:02: 01:00: 00:00: 00:00: 00:00: 00:00: 00:00: ff:ff: 01:ab
