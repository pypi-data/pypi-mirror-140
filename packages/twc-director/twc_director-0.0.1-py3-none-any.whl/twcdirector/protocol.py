# Commands B1, B2 and SLIP escape gathered from https://teslamotorsclub.com/tmc/threads/new-wall-connector-load-sharing-protocol.72830/page-25
# SLIP escape process from https://en.wikipedia.org/wiki/Serial_Line_Internet_Protocol

from enum import IntEnum
from ctypes import BigEndianStructure
import ctypes
import logging


_LOGGER = logging.getLogger(__name__)


class ChecksumMismatchError(Exception):
    pass


class DecoderNotFoundError(Exception):
    pass


class EncoderNotFoundError(Exception):
    pass


class Markers(IntEnum):
    START = 0xC0
    END = 0xC0
    END_TYPE = 0xFC


class MarkerEscape(IntEnum):
    ESCAPE = 0xDB
    ESCAPE_END = 0xDC
    ESCAPE_ESCAPE = 0xDD


class Status(IntEnum):
    READY = 0x00
    CHARGING = 0x01
    ERROR = 0x02
    WAITING = 0x03
    NEGOTIATING = 0x04
    MAX_CHARGE = 0x05
    ADJUSTING = 0x06
    CHARGING_CAR_LOW = 0x07
    CHARGE_STARTED = 0x08
    SETTING_LIMIT = 0x09
    ADJUSTMENT_COMPLETE = 0x0A
    UNKNOWN = 0xFF


class StatusCommands(IntEnum):
    GET_STATUS = 0x00
    SET_INCREASE_CURRENT = 0x06
    SET_DECREASE_CURRENT = 0x07
    SET_INITIAL_CURRENT = 0x05
    SET_SESSION_CURRENT = 0x09


class Commands(IntEnum):
    TWC_EMPTY = 0x00
    TWC_CLOSE_CONTACTORS = 0xB1
    TWC_OPEN_CONTACTORS = 0xB2
    TWC_STATUS = 0xE0
    TWC_CONTROLLER = 0xE1
    TWC_PERIPHERAL = 0xE2
    TWC_METER = 0xEB
    TWC_VERSION = 0xEC
    TWC_SERIAL = 0xED
    TWC_VIN_HIGH = 0xEE
    TWC_VIN_MID = 0xEF
    TWC_VIN_LOW = 0xF1


class MessageType(IntEnum):
    TWC_DATA_REQUEST = 0xFB
    TWC_COMMAND = 0xFC
    TWC_DATA = 0xFD


class TWCProtocol:
    class StartFrame(BigEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("start", ctypes.c_uint8),
            ("type", ctypes.c_uint8),
            ("command", ctypes.c_uint8),
            ("sender", ctypes.c_uint16)
        ]

    class EndFrame(BigEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("checksum", ctypes.c_uint8),
            ("end", ctypes.c_uint8),
            ("type", ctypes.c_uint8)
        ]

    class SerialData(BigEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("serial", ctypes.c_uint8 * 15)
        ]

    class MeterData(BigEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("total_kwh", ctypes.c_uint32),
            ("phase_l2_v", ctypes.c_uint8),
            ("phase_l1_v", ctypes.c_uint8),
            ("phase_l3_v", ctypes.c_uint8),
            ("separator", ctypes.c_uint16),
            ("phase_l2_i", ctypes.c_uint8),
            ("phase_l1_i", ctypes.c_uint8),
            ("phase_l3_i", ctypes.c_uint8),
            ("padding", ctypes.c_uint8 * 3)
        ]

    class VersionData(BigEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("version_release", ctypes.c_uint8),
            ("version_major", ctypes.c_uint8),
            ("version_minor", ctypes.c_uint8),
            ("version_patch", ctypes.c_uint8),
            ("padding", ctypes.c_uint8 * 7)
        ]

    class StatusData(BigEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("controller", ctypes.c_uint16),
            ("charge_state", ctypes.c_uint8),
            ("current_available", ctypes.c_uint16),
            ("current_delivered", ctypes.c_uint16)
        ]

    class PeripheralNegotiation(BigEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("session", ctypes.c_uint8),
            ("current_available", ctypes.c_uint16)
        ]

    class ControllerNegotiation(BigEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("session", ctypes.c_uint8),
            ("padding", ctypes.c_uint8 * 10)
        ]

    class RequestData(BigEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("recipient", ctypes.c_uint16),
            ("padding", ctypes.c_uint8 * 9)
        ]

    class StatusCommand(BigEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("recipient", ctypes.c_uint16),
            ("command", ctypes.c_uint8),
            ("command_arg", ctypes.c_uint16),
            ("padding", ctypes.c_uint8 * 6)
        ]

    start_frame_size = ctypes.sizeof(StartFrame)
    end_frame_size = ctypes.sizeof(EndFrame)
    frame_encapsulation_size = start_frame_size + end_frame_size

    def calculate_checksum(self, message):
        return sum(message[2:-3]) & 0xFF

    def escape_payload(self, payload):
        escaped_payload = bytearray()

        for byte in payload:
            if byte == Markers.START:
                escaped_payload.append(bytearray[MarkerEscape.ESCAPE, MarkerEscape.ESCAPE_END])
            elif byte == MarkerEscape.ESCAPE:
                escaped_payload.append(bytearray[MarkerEscape.ESCAPE, MarkerEscape.ESCAPE_ESCAPE])
            else:
                escaped_payload.append(byte)

        return escaped_payload

    def unescape_payload(self, payload):
        unescaped_payload = bytearray()

        payload_iterator = iter(payload)

        try:
            for byte in payload_iterator:
                if byte == MarkerEscape.ESCAPE:
                    escape_byte = next(payload_iterator)

                    if escape_byte == MarkerEscape.ESCAPE_END:
                        unescaped_payload.append(Markers.START)
                    elif escape_byte == MarkerEscape.ESCAPE_ESCAPE:
                        unescaped_payload.append(MarkerEscape.ESCAPE)
                else:
                    unescaped_payload.append(byte)
        except StopIteration:
            pass

        return unescaped_payload

    def extract_command_data(self, message):
        message_len = len(message)
        message_header = None
        message_terminator = None
        escaped_payload = b''
        payload = b''

        if message_len >= self.frame_encapsulation_size:
            message_header = self.StartFrame.from_buffer_copy(message)
            message_terminator = self.EndFrame.from_buffer_copy(message[-3:])

            escaped_payload = message[self.start_frame_size:-self.end_frame_size]
            payload = self.unescape_payload(escaped_payload)
            message = message[0:self.start_frame_size] + payload + message[-self.end_frame_size:]

            checksum = self.calculate_checksum(message)
            if message_terminator.checksum != checksum:
                raise ChecksumMismatchError(f"""Message checksum 0x{message_terminator.checksum:02X} does not match calculated checksum 0x{checksum:02X}""")
        else:
            raise IndexError(f"Message too short to process header, was {message_len}, should be at least {ctypes.sizeof(self.StartFrame)}")

        decoder = self._commands.get(message_header.command, None)
        data = None

        try:
            if decoder is not None:
                if message_header.type == MessageType.TWC_DATA:
                    data = decoder["decode"].from_buffer_copy(payload)
                elif message_header.type == MessageType.TWC_DATA_REQUEST:
                    data = decoder["request_decode"].from_buffer_copy(payload)
        except Exception as error:
            raise IndexError(f"""{error}, Command 0x{message_header.command:02X}, Type 0x{message_header.type:02X}, failed to decode. Length: {len(message[self.start_frame_size:-self.end_frame_size])}, Data: |{message[self.start_frame_size:-self.end_frame_size].hex().upper()}| """)

        return message_header, message_terminator, data

    def get_command_name(self, command):
        return self._commands.get(command, {}).get("name", "Unknown Command")

    def decode(self, command, data):
        try:
            return self._commands[command].get("decoder").from_buffer(data)
        except KeyError as error:
            raise DecoderNotFoundError(f"""Decoder for 0x{command:02X} not found.""")

    def encode(self, command, data):
        try:
            structure = self._commands[command].get("encoder")()
            for element in structure._fields_:
                setattr(structure, element[0], data[element[0]])
            return structure
        except (TypeError, KeyError) as error:
            raise EncoderNotFoundError(f"""Encoder for 0X{command:02X} not found.""")

    def request_encode(self, command, data):
        try:
            structure = self._commands[command].get("request_encoder")()
            for element in structure._fields_:
                setattr(structure, element[0], data[element[0]])
            return structure
        except (TypeError, KeyError) as error:
            raise EncoderNotFoundError(f"""Encoder for 0x{command:02X} not found.""")

    _commands = {
        Commands.TWC_SERIAL: {
            "name": "Unit Serial Number",
            "decode": SerialData,
            "encoder": SerialData,
            "request_decode": RequestData,
            "request_encoder": RequestData
        },
        Commands.TWC_VIN_HIGH: {
            "name": "Vehicle VIN first section",
            "decode": SerialData,
            "encoder": SerialData,
            "request_decode": RequestData,
            "request_encoder": RequestData
        },
        Commands.TWC_VIN_MID: {
            "name": "Vehicle VIN mid section",
            "decode": SerialData,
            "encoder": SerialData,
            "request_decode": RequestData,
            "request_encoder": RequestData
        },
        Commands.TWC_VIN_LOW: {
            "name": "Vehicle VIN end section",
            "decode": SerialData,
            "encoder": SerialData,
            "request_decode": RequestData,
            "request_encoder": RequestData
        },
        Commands.TWC_STATUS: {
            "name": "Unit status",
            "decode": StatusData,
            "encoder": RequestData,
            "request_decode": StatusCommand,
            "request_encoder": RequestData
        },
        Commands.TWC_METER: {
            "name": "Unit power delivery meter and voltage",
            "decode": MeterData,
            "encoder": MeterData,
            "request_decode": RequestData,
            "request_encoder": RequestData
        },
        Commands.TWC_VERSION: {
            "name": "Unit firmware version",
            "decode": VersionData,
            "encoder": VersionData,
            "request_decode": RequestData,
            "request_encoder": RequestData
        },
        Commands.TWC_PERIPHERAL: {
            "name": "Unit Peripheral Negotiation",
            "decode": PeripheralNegotiation,
            "encoder": ControllerNegotiation,
            "request_decode": RequestData,
            "request_encoder": RequestData
        },
        Commands.TWC_CONTROLLER: {
            "name": "Unit Peripheral Negotiation",
            "decode": ControllerNegotiation,
            "encoder": ControllerNegotiation,
            "request_decode": RequestData,
            "request_encoder": RequestData
        }
    }

