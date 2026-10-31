import struct

TYPES = {"int32": "<i", "float": "<f", "double": "<d"}


def parse_value(type_name, text):
    if type_name == "int32":
        return int(text)
    return float(text)


def pack(type_name, value):
    return struct.pack(TYPES[type_name], value)


def unpack(type_name, data):
    return struct.unpack(TYPES[type_name], data)[0]


def size_of(type_name):
    return struct.calcsize(TYPES[type_name])
