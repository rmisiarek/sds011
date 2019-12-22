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
    checksum: int = 1
    tail: int = Byte.Tail
    message: bytearray = field(init=False)

    def __post_init__(self):
        checksum = 0
        msg = bytearray()
        for key, value in self.__dict__.items():
            # checksum += value
            # if key == "checksum":
            #     msg.append(checksum % 256)
            # else:
            msg.append(value)
        self.message = msg


def firmware_version():
    return Packet(data1=Command.CommunicationMode, data2=CommandMode.Set)
