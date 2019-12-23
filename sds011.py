import logging
import struct

import serial

from packet import *

logging.basicConfig(
    format="%(asctime)s : %(levelname)s\t%(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    level=logging.DEBUG
)
logging.getLogger(__name__)


class Sender:

    response = None

    def __init__(self, device):
        self.device = device

    def communicate(self, packet):
        if not isinstance(packet.data1, Command):
            raise TypeError(f"CommandMode have to be type of {Command}")

        if not isinstance(packet.data2, CommandMode):
            raise TypeError(f"CommandValue have to be type of {CommandMode}")

        response = self._send(message=packet.message)

        if response and response[BytePosition.Data1] == packet.data1:
            self.response = response
            logging.debug(f"{packet.command_id=}, {packet.data1=}, {packet.data2=}, response = {response}")
            return self.response
        return None

    def _send(self, message: bytearray):
        print(f"sending: {message}")
        sent = self.device.write(message)
        self.device.flush()
        if sent != Length.Command.value:
            raise IOError(f"SDS011: sent {sent} bytes, expected {Length.Command.value} bytes")
        response = self._response()
        return response

    def _response(self):
        def valid_passiv_response(_bytes: bytes) -> bool:
            return (_bytes[0] == Byte.Head) and (_bytes[1] == Byte.PassivResponse)

        def valid_initiative_response(_bytes: bytes) -> bool:
            return (_bytes[0] == Byte.Head) and (_bytes[1] == Byte.InitiativeResponse)

        while True:
            received_bytes = self.device.read(Length.Response)
            if len(received_bytes) != Length.Response.value:
                raise IOError(f"SDS011: received {len(received_bytes)} bytes, expected {Length.Response.value} bytes")

            # TODO: validate checksum of response

            print(f"\rresponse: {struct.unpack('BBBBBBBBBB', received_bytes)}")

            if not valid_passiv_response(_bytes=received_bytes[0:2]):
                break
            else:
                pass
                # logging.debug(f"[ PassivResponse ] {received_bytes=}, {struct.unpack('BBBBBBBBBB', received_bytes)=}")
                # logging.info(f"SDS011: got response [ P ]: {received_bytes}")

            if not valid_initiative_response(_bytes=received_bytes[0:2]):
                break
            else:
                logging.debug(f"[ InitiativeResponse ] {received_bytes=}, {struct.unpack('BBBBBBBBBB', received_bytes)}")
                # logging.info(f"SDS011: got response [ I ]: {received_bytes}")

        return struct.unpack('BBBBBBBBBB', received_bytes)


class SDS011:
    def __init__(self, device_port):
        self.sender = None
        self._unit = "µg/m³"
        self._firmware = None
        self._device_id = None
        self._work_mode = None
        self._communication_mode = None

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
            self.sender = Sender(self.device)
            self.get_config(print_config=True)

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
            return "{0:02d}{1:02d}{2:02d}".format(response[3], response[4], response[5])
        return None

    def device_id(self):
        response = self.sender.communicate(get_device_id())
        if response:
            return "{0:02d}{1:02d}".format(response[BytePosition.Data5], response[BytePosition.Data6])
        return None

    def work_mode(self):
        response = self.sender.communicate(get_work_mode())
        if response:
            return "{0:02d}{1:02d}".format(response[BytePosition.Data5], response[BytePosition.Data6])
        return None

    def communication_mode(self):
        response = self.sender.communicate(get_communication_mode())
        if response:
            return response[BytePosition.Data3]
        return None

    def duty_cycle(self):
        response = self.sender.communicate(get_duty_cycle_packet())
        if response:
            print(f"\t\tduty_cycle = {response}")
        return None

    def set_duty_cycle(self, period: int):
        response = self.sender.communicate(set_duty_cycle_packet(period=period))
        if response:
            print(f"set_duty_cycle response {response}")
        return None

    def set_communication_mode(self):
        response = self.sender.communicate(set_communication_mode_packet())
        if response:
            print(f"set_communication_mode response {response}")
        return None


# def test_communication_mode(s):
#     s.communication_mode = CommunicationMode.Active
#     assert s.communication_mode == CommunicationMode.Active
#     s.communication_mode = CommunicationMode.Passive
#     assert s.communication_mode == CommunicationMode.Passive


if __name__ == "__main__":
    sensor = SDS011("/dev/ttyUSB0")
    sensor.duty_cycle()
    # sensor.set_communication_mode()
    sensor.set_duty_cycle(0)
    sensor.duty_cycle()
