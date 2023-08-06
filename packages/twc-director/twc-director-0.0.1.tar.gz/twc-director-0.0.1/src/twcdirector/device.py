import ctypes
import inspect
import logging
import random
import asyncio

from typing import Dict

from enum import IntFlag, auto

from .protocol import Commands, TWCProtocol, MessageType, Markers, StatusCommands, Status


_LOGGER = logging.getLogger(__name__)


class StatusDataFlag(IntFlag):
    VERSION = auto()
    SERIAL = auto()
    VIN_H = auto()
    VIN_M = auto()
    VIN_L = auto()
    INIT_DATA_RECEIVED = VERSION | SERIAL
    VIN = VIN_H | VIN_M | VIN_L


class TWCPeripheral:
    """TWCController Device"""
    def __init__(self, address=None, max_current=3200, command_queue=None, transmit_queue=None, device_initialised_callback=None):
        self._address = address
        self._protocol: TWCProtocol = TWCProtocol()
        self._max_current = max_current
        self._setpoint_current = self._max_current
        self._command_queue = command_queue
        self._transmit_queue = transmit_queue
        self._device_initialised_callback = device_initialised_callback
        self._is_processing_messages = False
        self._processing_task = None
        self._new_device = True
        self._restart_counter = 0
        self._status_data_received = 0x00

        self._session_id = random.randint(1, 254)

        self._device_data = {}
        self._device_data_updated_callbacks = {}

        _LOGGER.info(f"Created TWC device for address {self._address:04X}")

        self._command_map = {
            MessageType.TWC_DATA: {
                Commands.TWC_PERIPHERAL: self._set_peripheral,
                Commands.TWC_STATUS: self._set_status,
                Commands.TWC_METER: self._set_meter,
                Commands.TWC_VERSION: self._set_version,
                Commands.TWC_SERIAL: self._set_serial,
                Commands.TWC_VIN_HIGH: self._set_vin_h,
                Commands.TWC_VIN_MID: self._set_vin_m,
                Commands.TWC_VIN_LOW: self._set_vin_l
            },
            MessageType.TWC_DATA_REQUEST: {
            },
            MessageType.TWC_COMMAND: {
            }
        }

    async def queue_transmit_message(self, message):
        if self._transmit_queue is not None:
            await self._transmit_queue.put(message)
            _LOGGER.debug(f"Queued message: {message}")
            return True
        else:
            _LOGGER.warning("No transmit queue set, message not sent")
            return False

    def register_device_data_updated_callback(self, callback_map: dict):
        for key, callback in callback_map.items():
            if callable(callback) and callback not in self._device_data_updated_callbacks.get(key, []):
                _LOGGER.debug(f"Registered callback {key}")
                self._device_data_updated_callbacks.setdefault(key, []).append(callback)

    def deregister_device_data_updated_callback(self, callback_map: dict):
        for key, callback in callback_map.items():
            if callback in self._device_data_updated_callbacks.get(key, []):
                self._device_data_updated_callbacks.get(key).remove(callback)

    def get_restart_counter(self):
        return self._restart_counter

    def get_address(self):
        return self._address

    def get_max_current(self):
        return self._max_current

    def get_setpoint_current(self):
        return self._setpoint_current

    def set_setpoint_current(self, current):
        if current > self._max_current:
            self._setpoint_current = self._max_current
        if current < 0:
            self._setpoint_current = 0
        else:
            self._setpoint_current = current

    def get_command_queue(self):
        return self._command_queue

    def _construct_message(self, type, command, encoded_data):
        message_header = self._protocol.StartFrame()
        message_terminator = self._protocol.EndFrame()

        message_header.start = Markers.START
        message_header.type = type
        message_header.command = command.value
        message_header.sender = self._address

        unescaped_payload = bytes(encoded_data)

        message_terminator.end = Markers.END
        message_terminator.type = Markers.END_TYPE

        message_data = bytearray(ctypes.sizeof(encoded_data) + self._protocol.start_frame_size + self._protocol.end_frame_size)
        message_data[0:] = bytes(message_header) + unescaped_payload + bytes(message_terminator)

        # set checksum (3rd last byte)
        message_data[-self._protocol.end_frame_size] = self._protocol.calculate_checksum(message_data)

        payload = self._protocol.escape_payload(unescaped_payload)
        message_data[self._protocol.start_frame_size:-self._protocol.end_frame_size] = payload

        return {"message": message_data}

    async def queue_status_command(self, recipient, status_command, arg):
        payload = self._protocol.StatusCommand()
        payload.recipient = recipient
        payload.command = status_command
        payload.command_arg = arg

        await self.queue_transmit_message(self._construct_message(MessageType.TWC_DATA_REQUEST, Commands.TWC_STATUS, payload))

    async def queue_query(self, recipient, query_command: Commands):
        payload = self._protocol.request_encode(query_command, {"recipient": recipient, "padding": (ctypes.c_uint8 * 9)()})

        await self.queue_transmit_message(self._construct_message(MessageType.TWC_DATA_REQUEST, query_command, payload))

    async def queue_controller_announce(self):
        payload = self._protocol.encode(Commands.TWC_CONTROLLER, {"session": self._session_id, "padding": (ctypes.c_uint8 * 10)()})

        await self.queue_transmit_message(self._construct_message(MessageType.TWC_COMMAND, Commands.TWC_CONTROLLER, payload))

    async def queue_controller_peripheral_discover(self):
        payload = self._protocol.encode(Commands.TWC_PERIPHERAL, {"session": self._session_id, "padding": (ctypes.c_uint8 * 10)()})

        await self.queue_transmit_message(self._construct_message(MessageType.TWC_DATA_REQUEST, Commands.TWC_PERIPHERAL, payload))

    async def queue_controller_peripheral_claim(self, recipient):
        payload = self._protocol.request_encode(Commands.TWC_STATUS, {"recipient": recipient, "padding": (ctypes.c_uint8 * 9)()})

        await self.queue_transmit_message(self._construct_message(MessageType.TWC_DATA_REQUEST, Commands.TWC_STATUS, payload))

    async def queue_vin_h_response(self):
        payload = self._protocol.encode(Commands.TWC_VIN_HIGH, {"serial": (ctypes.c_uint8 * 15)()})

        await self.queue_transmit_message(self._construct_message(MessageType.TWC_DATA, Commands.TWC_VIN_HIGH, payload))

    async def queue_vin_m_response(self):
        payload = self._protocol.encode(Commands.TWC_VIN_MID, {"serial": (ctypes.c_uint8 * 15)()})

        await self.queue_transmit_message(self._construct_message(MessageType.TWC_DATA, Commands.TWC_VIN_MID, payload))

    async def queue_vin_l_response(self):
        payload = self._protocol.encode(Commands.TWC_VIN_LOW, {"serial": (ctypes.c_uint8 * 15)()})

        await self.queue_transmit_message(self._construct_message(MessageType.TWC_DATA, Commands.TWC_VIN_LOW, payload))

    async def queue_serial_response(self):
        data = {"serial": (ctypes.c_uint8 * 15)()}

        if self._status_data_received & StatusDataFlag.VERSION:
            for index, character in enumerate(self.get_serial()):
                data["serial"][index] = ord(character)
        else:
            for index, character in enumerate("A19K000F00D"):
                data["serial"][index] = ord(character)

        payload = self._protocol.encode(Commands.TWC_SERIAL, data)
        await self.queue_transmit_message(self._construct_message(MessageType.TWC_DATA, Commands.TWC_SERIAL, payload))

    async def queue_meter_response(self):
        data = {"total_kwh": 10, "phase_l2_v": 0, "phase_l1_v": 240, "phase_l3_v": 0,
                "separator": 0, "phase_l2_i": 0, "phase_l1_i": 0, "phase_l3_i": 0, "padding": (ctypes.c_uint8 * 3)()}

        payload = self._protocol.encode(Commands.TWC_METER, data)
        await self.queue_transmit_message(self._construct_message(MessageType.TWC_DATA, Commands.TWC_METER, payload))

    async def queue_version_response(self):
        if self._status_data_received & StatusDataFlag.VERSION:
            payload = self._protocol.encode(Commands.TWC_VERSION, {**self._device_data, "padding": (ctypes.c_uint8 * 7)()})
        else:
            payload = self._protocol.encode(Commands.TWC_VERSION, {"version_release": 0x04,
                                                                   "version_major": 0x05,
                                                                   "version_minor": 0x03,
                                                                   "version_patch": 0x02,
                                                                   "padding": (ctypes.c_uint8 * 7)()})

        await self.queue_transmit_message(self._construct_message(MessageType.TWC_DATA, Commands.TWC_VERSION, payload))

    def set_processing_task(self, task):
        self._processing_task = task

    def stop_processing_messages(self):
        self._is_processing_messages = False

        if self._command_queue:
            self._command_queue.put_nowait({})

        if self._processing_task:
            self._processing_task.cancel()

        return self._processing_task

    def _string_decode(self, data):
        serial = bytearray(data.serial).decode("utf-8", "ignore")
        # Remove null termination in underlying buffer
        try:
            serial = serial[:serial.index("\x00")]
        except ValueError:
            serial = ""

        return serial

    def _set_vin_h(self, data):
        self._device_data["vin_h"] = self._string_decode(data)

        if len(self._device_data["vin_h"]) == 0:
            self._status_data_received &= ~StatusDataFlag.VIN_H
        else:
            self._status_data_received |= StatusDataFlag.VIN_H

    def _set_vin_m(self, data):
        self._device_data["vin_m"] = self._string_decode(data)

        if len(self._device_data["vin_m"]) == 0:
            self._status_data_received &= ~StatusDataFlag.VIN_M
        else:
            self._status_data_received |= StatusDataFlag.VIN_M

    def _set_vin_l(self, data):
        self._device_data["vin_l"] = self._string_decode(data)

        if len(self._device_data["vin_l"]) == 0:
            self._status_data_received &= ~StatusDataFlag.VIN_L
        else:
            self._status_data_received |= StatusDataFlag.VIN_L

    def get_vin(self):
        if self.is_car_connected():
            return self._device_data.get("vin_h") + self._device_data.get("vin_m") + self._device_data.get("vin_l")
        else:
            return "No Car Connected"

    def is_car_connected(self):
        previous_state = self._device_data.get("car_connected", False)

        if (self._status_data_received & StatusDataFlag.VIN) == StatusDataFlag.VIN:
            self._device_data["car_connected"] = True
        else:
            self._device_data["car_connected"] = False

        if previous_state != self._device_data["car_connected"]:
            asyncio.get_event_loop().create_task(self._process_callbacks("TWC_CAR_CONNECTED", self._device_data_updated_callbacks.get("TWC_CAR_CONNECTED", [])))

        return self._device_data["car_connected"]

    def _set_serial(self, data):
        self._device_data["serial"] = self._string_decode(data)
        self._status_data_received |= StatusDataFlag.SERIAL

        if (self._status_data_received & StatusDataFlag.INIT_DATA_RECEIVED) == StatusDataFlag.INIT_DATA_RECEIVED:
            self._device_initialised()

    def get_serial(self):
        return self._device_data.get("serial", "Discovering")

    def _set_version(self, data):
        self._device_data["version_release"] = data.version_release
        self._device_data["version_major"] = data.version_major
        self._device_data["version_minor"] = data.version_minor
        self._device_data["version_patch"] = data.version_patch
        self._device_data["version"] = f"""{data.version_release}.{data.version_major}.{data.version_minor}.{data.version_patch}"""
        self._status_data_received |= StatusDataFlag.VERSION

        if (self._status_data_received & StatusDataFlag.INIT_DATA_RECEIVED) == StatusDataFlag.INIT_DATA_RECEIVED:
            self._device_initialised()

    def get_version(self):
        return self._device_data.get("version", "Discovering")

    def get_device_data(self):
        return self._device_data

    def _set_meter(self, data):
        self._device_data["total_kwh"] = data.total_kwh
        self._device_data["voltage_phase_l1"] = data.phase_l1_v
        self._device_data["voltage_phase_l2"] = data.phase_l2_v
        self._device_data["voltage_phase_l3"] = data.phase_l3_v
        self._device_data["current_phase_l1"] = data.phase_l1_i / 2.0
        self._device_data["current_phase_l2"] = data.phase_l2_i / 2.0
        self._device_data["current_phase_l3"] = data.phase_l3_i / 2.0

        _LOGGER.debug(f"Total kWh is {data.total_kwh}")

    def get_meter_total_kwh(self):
        return self._device_data.get("total_kwh", 0)

    def get_meter_voltage_phase_l1(self):
        return self._device_data.get("voltage_phase_l1", 0)

    def get_meter_current_phase_l1(self):
        return self._device_data.get("current_phase_l1", 0)

    def _set_status(self, data):
        self._device_data["charge_state"] = data.charge_state
        self._device_data["current_available"] = data.current_available
        self._device_data["current_delivered"] = data.current_delivered

    def get_status_charge_state(self):
        return Status(self._device_data.get("charge_state", 0xFF))

    def get_status_current_available(self):
        return self._device_data.get("current_available", 0)

    def get_status_current_delivered(self):
        return self._device_data.get("current_delivered", 0)

    def _set_peripheral(self, data):
        if not self._new_device and self._session_id != data.session:
            self._restart_counter += 1

        self._session_id = data.session
        self._device_data["default_current_available"] = data.current_available

    def _device_initialised(self):
        if self._new_device:
            self._new_device = False
            if self._device_initialised_callback:
                self._device_initialised_callback(self)

    def get_session_id(self):
        return self._session_id

    def get_default_current_available(self):
        return self._device_data.get("default_current_available", 0) / 100

    async def _process_callbacks(self, callback_name, callbacks):
        for callback in callbacks:
            _LOGGER.debug(f"Called callbacks for {callback_name}")
            try:
                if inspect.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception:
                _LOGGER.exception(f"Callback for {callback_name} raised an exception")

    async def process_messages(self):
        _LOGGER.debug(f"Starting message processor for {self._address:04X}")

        if not self._command_queue:
            raise RuntimeError("Command queue not setup, can not process incoming messages")

        self._is_processing_messages = True

        while self._is_processing_messages:
            command_message = await self._command_queue.get()

            if not command_message:
                self._command_queue.task_done()
                continue

            try:
                _LOGGER.debug(f"{self._address:04X} Got Command Message for command 0x{command_message['command']:02X}")

                type = command_message["type"]
                command = command_message["command"]
                callback_name = command.name

                _LOGGER.debug(f"{self._address:08x} Processing {callback_name}")

                try:
                    command_processor = self._command_map[type].get(command, None)

                    if command_processor is not None:
                        command_processor(command_message["data"])

                    if hasattr(command_message["data"], "index"):
                        index = command_message['data'].index
                        callback_name = f"{command.name}__{index}"

                except KeyError as error:
                    _LOGGER.error(f"""Retrieving command processor for 0x{type:02X} - 0x{command:02X} failed. {error}""")
                except AttributeError as error:
                    _LOGGER.error(error)
                except Exception as error:
                    _LOGGER.exception(error)

                _LOGGER.debug(f"Checking callbacks for {callback_name}")
                await self._process_callbacks(callback_name, self._device_data_updated_callbacks.get(callback_name, []))
                await self._process_callbacks(callback_name, self._device_data_updated_callbacks.get("__ALL_UPDATES__", []))
            except Exception as error:
                # Catch and log all errors
                _LOGGER.exception(error)

            self._command_queue.task_done()

        _LOGGER.info(f"{self._address:04x} Stopped processing commands")

        return True


class TWCController(TWCPeripheral):
    def __init__(self, address=None, shared_max_current=3200, command_queue=None, transmit_queue=None, device_initialised_callback=None):
        super().__init__(address=address,
                         command_queue=command_queue,
                         transmit_queue=transmit_queue,
                         device_initialised_callback=device_initialised_callback)

        self._peripheral_devices: Dict[str, TWCPeripheral] = {}
        self._peripheral_last_state: Dict[str, int] = {}

        self._shared_max_current = shared_max_current

        self._controller_task = None

        self._query_command_list = [Commands.TWC_METER, Commands.TWC_SERIAL,
                                    Commands.TWC_VERSION, Commands.TWC_VIN_HIGH,
                                    Commands.TWC_VIN_MID, Commands.TWC_VIN_LOW]

    def register_peripheral(self, peripheral: TWCPeripheral):
        self._peripheral_devices[peripheral.get_address()] = peripheral
        self._peripheral_last_state[peripheral.get_address()] = peripheral.get_status_charge_state()

        peripheral.register_device_data_updated_callback({
            Commands.TWC_STATUS.name: lambda: self.monitor_peripheral_state(peripheral)
        })

    def monitor_peripheral_state(self, peripheral: TWCPeripheral):
        if peripheral and peripheral.get_address() in self._peripheral_last_state:
            if peripheral.get_status_charge_state() == Status.NEGOTIATING and self._peripheral_last_state != Status.NEGOTIATING:
                asyncio.get_event_loop().create_task(self.queue_peripheral_initial_current_command(peripheral.get_address(), peripheral.get_setpoint_current()))

            self._peripheral_last_state[peripheral.get_address()] = peripheral.get_status_charge_state()

    def set_shared_max_current(self, current):
        if current < 0:
            self._shared_max_current = 0
        else:
            self._shared_max_current = current

    def get_shared_max_current(self):
        return self._shared_max_current

    async def queue_peripheral_session_current_command(self, recipient, current):
        if 0 <= current <= self._shared_max_current:
            await self.queue_status_command(recipient, StatusCommands.SET_SESSION_CURRENT, current)

    async def queue_peripheral_initial_current_command(self, recipient, current):
        if 0 <= current <= self._shared_max_current:
            await self.queue_status_command(recipient, StatusCommands.SET_INITIAL_CURRENT, current)

    async def queue_peripheral_decrease_current_command(self, recipient):
        await self.queue_status_command(recipient, StatusCommands.SET_DECREASE_CURRENT, 0x0000)

    async def queue_peripheral_increase_current_command(self, recipient):
        await self.queue_status_command(recipient, StatusCommands.SET_INCREASE_CURRENT, 0x0000)

    async def queue_peripheral_close_contactors_command(self, recipient):
        payload = self._protocol.StatusCommand()
        payload.recipient = recipient
        payload.command = 0x00
        payload.command_arg = 0x00

        await self.queue_transmit_message(self._construct_message(MessageType.TWC_COMMAND, Commands.TWC_CLOSE_CONTACTORS, payload))

    async def queue_peripheral_open_contactors_command(self, recipient):
        payload = self._protocol.StatusCommand()
        payload.recipient = recipient
        payload.command = 0x00
        payload.command_arg = 0x00

        await self.queue_transmit_message(self._construct_message(MessageType.TWC_COMMAND, Commands.TWC_OPEN_CONTACTORS, payload))

    async def announce(self):
        message_count: int = 0

        timings = [1.300, 0.900, 0.900, 1.000, 0.600]

        while message_count < 5:
            await self.queue_controller_announce()
            await asyncio.sleep(timings[message_count])
            message_count += 1

        message_count = 0

        while message_count < 3:
            await self.queue_controller_peripheral_discover()
            await asyncio.sleep(0.400)
            message_count += 1

    def set_controller_task(self, task):
        self._controller_task = task

    async def claim_peripheral(self, peripheral: TWCPeripheral):
        message_count = 0

        if self.get_address() != peripheral.get_address():
            while message_count < 3:
                await self.queue_controller_peripheral_claim(peripheral.get_address())
                await asyncio.sleep(0.32)
                message_count += 1

    async def fake_controller_scheduler(self):
        query_command_index = 0

        while self._is_processing_messages:
            query_command = self._query_command_list[query_command_index]

            for peripheral in list(self._peripheral_devices.values()):
                await self.queue_query(peripheral.get_address(), query_command)
                await asyncio.sleep(0.32)
                await self.queue_controller_peripheral_claim(peripheral.get_address())
                await asyncio.sleep(0.32)

            query_command_index += 1

            if query_command_index >= len(self._query_command_list):
                query_command_index = 0

            await asyncio.sleep(0.900)
