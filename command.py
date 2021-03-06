from enum import IntEnum


class BytePosition(IntEnum):
    Head = 0,
    CommandID = 1,
    Data1 = 2,
    Data2 = 3,
    Data3 = 4,
    Data4 = 5,
    Data5 = 6,
    Data6 = 7,
    Data7 = 8,
    Data8 = 9,
    Data9 = 10,
    Data10 = 11,
    Data11 = 12,
    Data12 = 13,
    Data13 = 14,
    Data14 = 15,
    Data15 = 16,
    Checksum = 17,
    Tail = 18


class Command(IntEnum):
    CommunicationMode = 2,      # set data reporting mode
    Query = 4,                  # query data command
    DeviceId = 5,               # device id
    WorkMode = 6,               # set sleep mode or work mode
    Firmware = 7,               # check firmware version
    DutyCycle = 8               # set working period


class Byte(IntEnum):
    Head = 0xAA,                # start of the single message
    Tail = 0xAB,                # end of the single message
    CommandID = 0xB4,           # command id
    CommandEnd = 0xFF           # end of the command
    ActiveResponse = 0xC0       # active communication mode
    PassiveResponse = 0xC5      # passive communication mode


class Length(IntEnum):
    Command = 19                # length of command message
    Response = 10               # length of response message


class CommandMode(IntEnum):
    Get = 0,                    # getter (e.g. firmware version)
    Set = 1                     # setter (e.g. sleeping mode)


class CommandValue(IntEnum):
    Sleeping = 0,               # WorkMode
    Measuring = 1               # WorkMode
    Active = 0,                 # CommunicationMode
    Passive = 1,                # CommunicationMode
