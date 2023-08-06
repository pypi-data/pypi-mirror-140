import logging

from datetime import datetime, timezone
from ..protocol import MessageType, Commands, Status

_LOGGER = logging.getLogger(__name__)


async def render_message(message_queue, logfile_suffix=None):
    datestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M")

    if logfile_suffix:
        logfile_name = f"""{datestamp}-twc-protocol-{logfile_suffix}.log"""
    else:
        logfile_name = f"""{datestamp}-twc-protocol.log"""

    with open(logfile_name, "w") as logfile:
        while True:
            message = await message_queue.get()

            if not message:
                message_queue.task_done()
                break

            try:
                message_header = message["message_header"]
                message_terminator = message["message_terminator"]
                data = message["data"]
                raw_message = message["raw_message"]
                running_time_ms = message["running_time_ms"]

                sender = message_header.sender
                command = message_header.command

                checksum = message_terminator.checksum

                if data is None:
                    data = "\x1b[48;5;208mNo Decoder\x1b[0m"
                elif message_header.type == MessageType.TWC_DATA:
                    if message_header.command in [Commands.TWC_SERIAL, Commands.TWC_VIN_HIGH, Commands.TWC_VIN_MID,
                                                  Commands.TWC_VIN_LOW]:
                        data = f"""{bytearray(data.serial).decode("utf-8", "ignore")}"""
                        data = data[:data.index("\x00")]
                    elif message_header.command in [Commands.TWC_STATUS]:
                        data = f"""Reporting to: 0x{data.controller:02X}, Status: {Status(data.charge_state).name} (0x{data.charge_state:02X}), Current Available: {data.current_available}, Current Delivered: {data.current_delivered}"""
                    elif message_header.command in [Commands.TWC_METER]:
                        data = f"""Total kWh delivered {data.total_kwh:>7}, Phase L1 {data.phase_l1_v:>3}V {data.phase_l1_i/2.0:>5}A, Phase L2 {data.phase_l2_v:>3}V {data.phase_l2_i/2.0:>5}A, Phase L3 {data.phase_l3_v:>3}V {data.phase_l3_i/2.0:>5}A"""
                    elif message_header.command == Commands.TWC_VERSION:
                        data = f"""Version: {data.version_release}.{data.version_major}.{data.version_minor}.{data.version_patch}"""
                    elif message_header.command == Commands.TWC_PERIPHERAL:
                        data = f"""Session ID: {data.session}, Current Available: {data.current_available}"""
                    elif message_header.command == Commands.TWC_PLUG_STATE:
                        data = f"""{data.data.hex()}"""

                    if message_header.command in [Commands.TWC_VIN_HIGH, Commands.TWC_VIN_MID, Commands.TWC_VIN_LOW] and not data:
                        data = "No Car Connected"
                elif message_header.type == MessageType.TWC_DATA_REQUEST:
                    if message_header.command == Commands.TWC_STATUS:
                        data = f"""Status request sent to 0x{data.recipient:02X} for {Commands(message_header.command).name} (0x{message_header.command:02X}), Command: 0x{data.command:02X}, Command Arg: 0x{data.command_arg:04X}"""
                    else:
                        data = f"""Request sent to 0x{data.recipient:02X} for {Commands(message_header.command).name} (0x{message_header.command:02X})"""

                logfile.write(f"""{running_time_ms:>12} {raw_message.hex().upper():<60} Len: {len(raw_message):>2} Sender: 0x{sender:04X}, Command: 0x{command:02X}, Checksum: 0x{checksum:02X}, Data: |{data}|\n""")
                logfile.flush()
            except Exception as error:
                _LOGGER.error(f"""Error occurred rendering log: {error}""")

            message_queue.task_done()

