import mido
import requests

SERVER_HOST = "localhost"

def debug():
    print("\nisChannelActive", isChannelActive)
    print("isChannelLive", isChannelLive)
    print("channelVolumeLevels", channelVolumeLevels, "\n")

def notifyisChannelLive(channelNumber, active):
    lampNumber = 0

    match channelNumber:
        case 1:
            lampNumber = 5
        case 2:
            lampNumber = 6
        case 3:
            lampNumber = 7
        case 4:
            lampNumber = 8
    
    if lampNumber == 0:
        return

    data = {
        "lampNumber": lampNumber,
        "active": active
    }

    requests.post(f"http://{SERVER_HOST}:25543/channelLive", json=data)

input("Is it set to default? ")

notifyisChannelLive(1, True)

input_ports = mido.get_input_names()

# Check if there are any available input ports
if not input_ports:
    print("No MIDI input ports found.")
    exit()

midi_id = 0

if len(input_ports) > 1:
    print("Available MIDI input ports:")
    for i, port in enumerate(input_ports):
        print(f"{i}: {port}")
    midi_id = int(input("\nPlease enter the ID of the MIDI Controller to use: "))
    exit()

# Open the first available MIDI input port
input_port_name = input_ports[midi_id]
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
                notifyisChannelLive(message.channel, isChannelLive[message.channel])

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
