from dataclasses import dataclass, field
from command import *


@dataclass
class Packet:
    head: int = Byte.Head
    command_id: int = Byte.CommandID
    data1: int = 0
    data2: int = 0
    data3: int = 0
    data4: int = 0
    data5: int = 0
    data6: int = 0
    data7: int = 0
    data8: int = 0
    data9: int = 0
    data10: int = 0
    data11: int = 0
    data12: int = 0
    data13: int = 0
    data14: int = Byte.CommandEnd
    data15: int = Byte.CommandEnd
    checksum: int = 0
    tail: int = Byte.Tail
    message: bytearray = field(init=False)

    def __post_init__(self):
        checksum = 0
        msg = bytearray()
        for key, value in self.__dict__.items():
            if key.startswith("data"):
                checksum += value
            if key == "checksum":
                msg.append(checksum % 256)
            else:
                msg.append(value)
        self.message = msg


def set_communication_mode_packet(communication_mode: CommandValue):
    return Packet(data1=Command.CommunicationMode, data2=CommandMode.Set, data3=communication_mode)


def get_communication_mode():
    return Packet(data1=Command.CommunicationMode, data2=CommandMode.Get)


def query_data():
    return Packet(data1=Command.Query, data2=CommandMode.Get)


def set_device_id(byte12: int, byte13: int):
    return Packet(data1=Command.DeviceId, data2=CommandMode.Set, data12=byte12, data13=byte13)


def get_device_id():
    return Packet(data1=Command.DeviceId, data2=CommandMode.Get)


def set_work_mode(work_mode: CommandValue):
    return Packet(data1=Command.WorkMode, data2=CommandMode.Set, data3=work_mode)


def get_work_mode():
    return Packet(data1=Command.WorkMode, data2=CommandMode.Get)


def set_duty_cycle(period: int = 0):
    if not 0 <= period <= 30:
        raise ValueError("'period' has to be between 0 and 30 value")
    return Packet(data1=Command.DutyCycle, data2=CommandMode.Set, data3=period)


def get_duty_cycle():
    return Packet(data1=Command.DutyCycle, data2=CommandMode.Get)


def get_firmware_version():
    return Packet(data1=Command.Firmware, data2=CommandMode.Get)
