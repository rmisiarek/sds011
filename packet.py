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


def get_firmware_version():
    return Packet(data1=Command.Firmware, data2=CommandMode.Get)


def get_device_id():
    return Packet(data1=Command.DeviceId, data2=CommandMode.Get)


def get_work_mode():
    return Packet(data1=Command.WorkMode, data2=CommandMode.Get)


def work_mode_measuring():
    return Packet(data1=Command.WorkMode, data2=CommandMode.Set, data3=CommandValue.Measuring)


def work_mode_sleeping():
    return Packet(data1=Command.WorkMode, data2=CommandMode.Set, data3=CommandValue.Sleeping)


def get_communication_mode():
    return Packet(data1=Command.CommunicationMode, data2=CommandMode.Get)


def set_communication_mode_packet():
    return Packet(data1=Command.CommunicationMode, data2=CommandMode.Set, data3=CommandValue.Active)


def query():
    pass


def get_duty_cycle_packet():
    return Packet(data1=Command.DutyCycle, data2=CommandMode.Get)


def set_duty_cycle_packet(period: int):
    # TODO: validate range of period, should be in 1-30
    return Packet(data1=Command.DutyCycle, data2=CommandMode.Set, data3=period)
