import asyncio
import sys
import signal
import curses
import argparse

from threading import Thread, Event
from typing import List

import logging
from .device import TWCController, TWCPeripheral
from .listener import TWCListener

from .collectors.logfile import render_message

_LOGGER = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="TWC Controller")
parser.add_argument("--port", required=False, help="RS485 Serial Port", default="/dev/ttySC0")
parser.add_argument("--disable-fake-controller", action="store_true", required=False, help="Disable fake controller functionality")
parser.add_argument("--log", action="store_true", required=False, help="Enable Logging")

args = parser.parse_args()


async def main(port="/dev/ttySC0", fake_controller=True, log_enable=False):
    device_list: List[DeviceWrapper] = []
    row_offset = 4

    logfile_suffix = port.split("/")[-1]

    loop = asyncio.get_event_loop()

    twc_listener = TWCListener(interface=port, event_loop=loop, enable_fake_controller=fake_controller)

    device_queue = asyncio.Queue()
    message_queue = None

    twc_listener.register_device_queue(device_queue)

    if log_enable:
        message_queue = asyncio.Queue()
        twc_listener.register_message_listener_queue(message_queue)
        message_log_task = asyncio.create_task(render_message(message_queue, logfile_suffix=logfile_suffix))

    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)

    for sig in signals:
        loop.add_signal_handler(sig, lambda sig=sig: asyncio.create_task(shutdown(twc_listener, message_queue)))

    message_tx_task = asyncio.create_task(twc_listener.listen())
    message_rx_task = asyncio.create_task(twc_listener.process_transmit_messages())

    print("\x1b[H\x1b[J\x1b[?25l")
    print("\x1b[H")
    print(f"""\x1b[{row_offset};4HSearching...""")

    await twc_listener.started_listening

    ui = consoleUI(row_offset, twc_listener, device_list)
    ui_thread = ui.start()

    while twc_listener.is_listening:
        new_device = await device_queue.get()

        if new_device:
            device_list.append(DeviceWrapper(new_device, len(device_list), row_offset, ui))
            ui.needs_refresh()

        device_queue.task_done()

    print("\x1b[H\x1b[J\x1b[?25h")
    print("Shutting down...")

    ui.shutdown()
    ui.join()


class DeviceWrapper:
    def __init__(self, device: TWCPeripheral, index, row_offset, ui):
        self._device: TWCPeripheral = device
        self._index = index
        self._row_offset = row_offset
        self._ui = ui
        self._device.register_device_data_updated_callback({
            "__ALL_UPDATES__": self.schedule_refresh
        })

    @property
    def index(self):
        return self._index

    @property
    def address(self):
        return self._device.get_address()

    @property
    def version(self):
        return self._device.get_version()

    @property
    def vin(self):
        return self._device.get_vin()

    @property
    def meter(self):
        return f"""Total kWh: {self._device.get_meter_total_kwh():>8}, {self._device.get_meter_voltage_phase_l1():>3}V {self._device.get_meter_current_phase_l1():>4}A"""

    @property
    def serial(self):
        return self._device.get_serial()

    @property
    def status(self):
        return f"""{self._device.get_status_charge_state().name:>15} A: {self._device.get_status_current_available():>5}A D: {self._device.get_status_current_delivered():>5}A"""

    def set_setpoint_current(self, current):
        self._device.set_setpoint_current(current)

    def schedule_refresh(self):
        self._ui.needs_refresh()


class consoleUI(Thread):
    def __init__(self, row_offset, listener, device_list: List[DeviceWrapper]):
        Thread.__init__(self, name="consoleUI")
        self._listener = listener
        self._is_reading = Event()
        self._row_offset = row_offset
        self._devices: List[DeviceWrapper] = device_list
        self._current_index = -1
        self._refresh_list = False
        self._loop = listener.get_event_loop()
        self._update_in_progress = False
        self._fake_controller: TWCController = listener.get_fake_controller()
        self._update_index = -1
        self._update_total = -1
        self._update_delay = 0
        self._update_type = None

    def shutdown(self):
        self._is_reading.clear()

    def needs_refresh(self):
        self._refresh_list = True

    def run(self):
        self._is_reading.set()

        screen = curses.initscr()
        curses.noecho()
        curses.raw()
        curses.cbreak()
        screen.keypad(True)
        curses.halfdelay(2)

        while self._is_reading.is_set():
            print(f"""\x1b[2;1H\x1b[0KFake Controller is {"enabled" if self._fake_controller else "not enabled"}""")

            try:
                key = screen.getkey()

                if key:
                    if key == "KEY_DOWN":
                        if self._current_index < (len(self._devices) - 1):
                            self._current_index += 1
                            self._refresh_list = True
                    elif key == "KEY_UP":
                        if len(self._devices) and self._current_index > 0:
                            self._current_index -= 1
                            self._refresh_list = True
                    elif key == "d":
                        if self._fake_controller and self._current_index >= 0:
                            address = self._devices[self._current_index].address
                            asyncio.run_coroutine_threadsafe(self._fake_controller.queue_peripheral_open_contactors_command(address), self._loop)
                    elif key == "c":
                        if self._fake_controller and self._current_index >= 0:
                            address = self._devices[self._current_index].address
                            asyncio.run_coroutine_threadsafe(self._fake_controller.queue_peripheral_close_contactors_command(address), self._loop)
                    elif key == "1":
                        if self._fake_controller and self._current_index >= 0:
                            device = self._devices[self._current_index]
                            device.set_setpoint_current(600)
                    elif key == "2":
                        if self._fake_controller and self._current_index >= 0:
                            device = self._devices[self._current_index]
                            device.set_setpoint_current(1000)
                    elif key == "3":
                        if self._fake_controller and self._current_index >= 0:
                            device = self._devices[self._current_index]
                            device.set_setpoint_current(2000)
                    elif key == "4":
                        if self._fake_controller and self._current_index >= 0:
                            device = self._devices[self._current_index]
                            device.set_setpoint_current(3200)
                    elif key == "5":
                        if self._fake_controller and self._current_index >= 0:
                            device = self._devices[self._current_index]
                            device.set_setpoint_current(0)
                    elif key == "+":
                        if self._fake_controller and self._current_index >= 0:
                            address = self._devices[self._current_index].address
                            asyncio.run_coroutine_threadsafe(self._fake_controller.queue_peripheral_increase_current_command(address), self._loop)
                    elif key == "-":
                        if self._fake_controller and self._current_index >= 0:
                            address = self._devices[self._current_index].address
                            asyncio.run_coroutine_threadsafe(self._fake_controller.queue_peripheral_decrease_current_command(address), self._loop)
                    elif key == "6":
                        if self._fake_controller and self._current_index >= 0:
                            address = self._devices[self._current_index].address
                            asyncio.run_coroutine_threadsafe(self._fake_controller.queue_peripheral_session_current_command(address, 600), self._loop)
                    elif key == "7":
                        if self._fake_controller and self._current_index >= 0:
                            address = self._devices[self._current_index].address
                            asyncio.run_coroutine_threadsafe(self._fake_controller.queue_peripheral_session_current_command(address, 1000), self._loop)
                    elif key == "8":
                        if self._fake_controller and self._current_index >= 0:
                            address = self._devices[self._current_index].address
                            asyncio.run_coroutine_threadsafe(self._fake_controller.queue_peripheral_session_current_command(address, 2000), self._loop)
                    elif key == "9":
                        if self._fake_controller and self._current_index >= 0:
                            address = self._devices[self._current_index].address
                            asyncio.run_coroutine_threadsafe(self._fake_controller.queue_peripheral_session_current_command(address, 3200), self._loop)
                    elif key == "0":
                        if self._fake_controller and self._current_index >= 0:
                            address = self._devices[self._current_index].address
                            asyncio.run_coroutine_threadsafe(self._fake_controller.queue_peripheral_session_current_command(address, 0), self._loop)

                    print(f"""\x1b[1;1H\x1b[0KCommand: {key}""".zfill(20))

            except curses.error:
                # Timeout pass
                pass

            if self._refresh_list:
                for index, device in enumerate(self._devices):
                    highlight = ""

                    if index == self._current_index:
                        highlight = "\x1b[7m"

                    print(f"""\x1b[{self._row_offset + device.index};4H{highlight}{device.address:04X}\x1b[0m  {device.serial:<12} {device.version:>12} {device.vin:>17} {device.status:>30} {device.meter}\x1b[0K""")

                self._refresh_list = False

        try:
            curses.nocbreak()
            screen.keypad(False)
            curses.noraw()
            curses.echo()
            curses.endwin()
        except Exception as error:
            _LOGGER.error(f"""Failed to de-initialise curses: {error}""")

        _LOGGER.info("""UI Shutdown...""")


async def shutdown(twc_listener, message_queue):
    await twc_listener.shutdown()

    if message_queue:
        message_queue.put_nowait({})


if __name__ == '__main__':
    try:
        logging.basicConfig(filename=f"""twc-director-{args.port.split("/")[-1]}-error.log""", filemode="w", level=logging.INFO)

        asyncio.run(main(port=args.port, fake_controller=not args.disable_fake_controller, log_enable=args.log))
    except asyncio.CancelledError as status:
        _LOGGER.info("Shut down.")

    sys.exit(0)
