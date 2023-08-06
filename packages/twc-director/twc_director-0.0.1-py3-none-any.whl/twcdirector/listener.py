"""TWC Protocol and Communications Library"""
import asyncio
import aioserial
import datetime

import logging

from .protocol import TWCProtocol, Commands, ChecksumMismatchError, Markers
from .device import TWCController, TWCPeripheral

from typing import Dict


_LOGGER = logging.getLogger(__name__)


class TWCListener:
    def __init__(self, interface="/dev/ttySC0", event_loop=None, enable_fake_controller=True, shared_max_current=600):
        self._devices: Dict[str, TWCPeripheral] = {}
        self._is_listening = asyncio.Event()
        self._is_processing_transmit_messages = False
        self._rs485_interface = interface
        self._protocol = TWCProtocol()

        self._shared_max_current = shared_max_current

        self._started_listening = asyncio.Event()
        self._has_shutdown = asyncio.Event()
        self._has_stopped_transmission = asyncio.Event()

        self._event_loop = event_loop
        self._rs485_bus = aioserial.AioSerial(self._rs485_interface, 9600, loop=event_loop)

        self._transmit_queue = asyncio.Queue()

        self._start_time = datetime.datetime.now()
        self._current_time = self._start_time
        self._running_time_ms = 0

        self._listeners = [
        ]

        self._new_device_queues = []

        self._fake_controller_is_claiming = asyncio.Event()
        self._fake_controller_claim_complete = asyncio.Event()

        self._fake_controller_is_claiming.clear()
        self._fake_controller_claim_complete.set()

        self._fake_controller: TWCController = None

        self._enable_fake_controller = enable_fake_controller

    @property
    def started_listening(self):
        return self._started_listening.wait()

    @property
    def is_listening(self):
        return self._is_listening.is_set()

    def get_device_list(self):
        return self._devices

    def get_event_loop(self):
        return self._event_loop

    def get_fake_controller(self):
        return self._fake_controller

    def register_device_queue(self, queue):
        if isinstance(queue, asyncio.Queue):
            self._new_device_queues.append(queue)

    def register_message_listener_queue(self, queue):
        if isinstance(queue, asyncio.Queue):
            self._listeners.append(queue)

    def device_initialised_callback(self, new_device):
        if not self._fake_controller or (self._fake_controller.get_address() != new_device.get_address()):
            for queue in self._new_device_queues:
                queue.put_nowait(new_device)

        _LOGGER.debug(f"Added device 0x{new_device.get_address():04X}")

    def _initialise_fake_controller(self, address=0xF00D):
        self._fake_controller = TWCController(address=address,
                                              command_queue=asyncio.Queue(),
                                              transmit_queue=self._transmit_queue,
                                              shared_max_current=self._shared_max_current)
        device_task = self._event_loop.create_task(self._fake_controller.process_messages())
        self._fake_controller.set_processing_task(device_task)
        controller_task = self._event_loop.create_task(self._fake_controller.fake_controller_scheduler())
        self._fake_controller.set_controller_task(controller_task)

    async def shutdown(self):
        _LOGGER.info("Shutting down")
        try:
            self._is_listening.clear()
            self._is_processing_transmit_messages = False

            if self._transmit_queue:
                self._transmit_queue.put_nowait({})

            await self._rs485_bus._cancel_read_async()
            self._rs485_bus.close()

            for queue in self._new_device_queues:
                queue.put_nowait({})

            tasks = []
            for device in self._devices.values():
                task = device.stop_processing_messages()
                if task:
                    tasks.append(task)

            if self._fake_controller:
                task = self._fake_controller.stop_processing_messages()

                if task:
                    tasks.append(task)

            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except asyncio.CancelledError:
                _LOGGER.info(f"""All tasks cancelled""")

            await self._has_stopped_transmission.wait()
            await self._has_shutdown.wait()
        except Exception as error:
            _LOGGER.error(f"""Error occurred shutting down: {error}""")

        return True

    async def process_transmit_messages(self):
        self._is_processing_transmit_messages = True

        while self._is_processing_transmit_messages is True:
            transmit_message = await self._transmit_queue.get()

            if transmit_message:
                await self._rs485_bus.write_async(transmit_message["message"])

            self._transmit_queue.task_done()

        self._has_stopped_transmission.set()
        return True

    async def listen(self):
        if self._enable_fake_controller:
            self._initialise_fake_controller()

        self._is_listening.set()
        self._started_listening.set()

        while self._is_listening.is_set():
            try:
                message = await self._rs485_bus.read_until_async(expected=b'\xC0')

                if not message:
                    continue

                if len(message) >= 16:
                    last_byte = await self._rs485_bus.read_async()

                self._current_time = datetime.datetime.now()
                self._running_time_ms = round((self._current_time - self._start_time).total_seconds() * 1000)

                if len(message) >= 16 and ((last_byte[0] & 0xF0) == 0xF0):
                    # Add start byte back in to aide decoding
                    message = bytes([Markers.START]) + message + last_byte
                    await self.process_message(message)

            except (KeyError, IndexError, ValueError, ChecksumMismatchError) as error:
                _LOGGER.error(error)
            except OSError as error:
                _LOGGER.info(f"""Read attempted during shutdown: {error}""")

        self._has_shutdown.set()
        return 0

    async def process_message(self, message):
        try:
            message_header, message_terminator, data = self._protocol.extract_command_data(message)

            sender = message_header.sender
            command = Commands(message_header.command)

            device = self._devices.get(sender, None)

            if device is None:
                device = TWCPeripheral(sender,
                                       command_queue=asyncio.Queue(),
                                       transmit_queue=self._transmit_queue,
                                       device_initialised_callback=self.device_initialised_callback)
                self._devices[sender] = device
                device_task = self._event_loop.create_task(device.process_messages())
                device.set_processing_task(device_task)

                if self._fake_controller:
                    self._fake_controller.register_peripheral(device)

            device.get_command_queue().put_nowait(
                {"type": message_header.type, "command": command, "data": data}
            )

            if command == Commands.TWC_PERIPHERAL and self._fake_controller:
                self._event_loop.create_task(self._fake_controller.claim_peripheral(device))

            for queue in self._listeners:
                queue.put_nowait({"running_time_ms": self._running_time_ms,
                                  "message_header": message_header,
                                  "message_terminator": message_terminator,
                                  "data": data,
                                  "raw_message": message})

        except (KeyError, IndexError, ValueError, ChecksumMismatchError) as error:
            _LOGGER.error(error)
