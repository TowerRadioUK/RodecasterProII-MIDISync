import mido
import asyncio
import aiohttp
import tomli
import tkinter.messagebox

VERSION = "1.0.0"
TITLE = f"Tower Radio MIDI Sync v{VERSION} - Licensed to harry@hwal.uk"

try:
    with open("config.toml", mode="rb") as fp:
        config = tomli.load(fp)
except FileNotFoundError:
    tkinter.messagebox.showerror(TITLE, "Unable to locate configuration file. config.toml was not found.")
    exit()


def debug():
    if config["other"]["debug"]:
        print("\nisChannelActive", isChannelActive)
        print("isChannelLive", isChannelLive)
        print("channelVolumeLevels", channelVolumeLevels, "\n")


async def notify_channel_live(channel_number, active):
    lamp_number = {
        1: 5,
        2: 6,
        3: 7,
        4: 8,
        5: 2,
        0: 4,  # FAULT
    }.get(channel_number)

    if not lamp_number:
        return

    data = {
        "lampNumber": lamp_number,
        "active": active,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://{config['clock']['host']}:{config['clock']['port']}/channelLive",
            json=data,
        ) as response:
            response.raise_for_status()  # Raise an exception for unsuccessful responses


if config["other"]["prompt_default"]:
    tkinter.messagebox.showwarning(
        TITLE,
        "Please ensure that all channels are set to loopback and the sliders are down before continuing. Press OK to continue.",
    )

# Reset to defaults
asyncio.run(notify_channel_live(1, True))
asyncio.run(notify_channel_live(2, True))
asyncio.run(notify_channel_live(3, True))
asyncio.run(notify_channel_live(4, True))
asyncio.run(notify_channel_live(5, False))
asyncio.run(notify_channel_live(0, False))

input_ports = mido.get_input_names()

# Check if there are any available input ports
if not input_ports:
    tkinter.messagebox.showerror(TITLE, "No MIDI input ports found. Please ensure that the Rodecaster Pro II is connected to this computer.")
    exit()

if config["other"]["debug"]:
    print("Available MIDI input ports:")
    for i, port in enumerate(input_ports):
        print(f"{i}: {port}")

# Open the first available MIDI input port
input_port_name = input_ports[config["midi"]["input_id"]]
with mido.open_input(input_port_name) as input_port:
    print(f"Listening on {input_port_name}...")

    # Mic 1, Mic 2, Mic 3, Mic 4, Main, Chat
    isChannelActive = [False, False, False, False, False, False]
    channelVolumeLevels = [0, 0, 0, 0, 0, 0]
    isChannelLive = [False, False, False, False, False, False]

    for message in input_port:
        # Mute button pressed
        if message.control == 27 and message.value == 1:
            # Toggle channel active
            isChannelActive[message.channel] = isChannelActive[message.channel]

            # If mute toggled, and slider is up
            if channelVolumeLevels[message.channel] >= 1:
                isChannelLive[message.channel] = isChannelActive[message.channel]
                asyncio.run(
                    notify_channel_live(message.channel, isChannelLive[message.channel])
                )

            # Chat channel - FAULT
            if message.channel == 5:
                asyncio.run(notify_channel_live(0, isChannelLive[message.channel]))

        # Volume slider moved
        if message.control == 15:
            # Set the volume level to the value of the slider
            channelVolumeLevels[message.channel] = message.value

            # If slider is up
            if message.value >= 1:
                isChannelLive[message.channel] = isChannelActive[message.channel]
            else:
                isChannelLive[message.channel] = False

        debug()
