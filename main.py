import mido

def debug():
    print("\nisChannelMuted", isChannelMuted)
    print("micLive",micLive)
    print("channelVolumeLevels", channelVolumeLevels,"\n")

input("Is it set to default? ")

# List all available MIDI input ports
print("Available MIDI input ports:")
input_ports = mido.get_input_names()
for i, port in enumerate(input_ports):
    print(f"{i}: {port}")

# Check if there are any available input ports
if not input_ports:
    print("No MIDI input ports found.")
    exit()

# Open the first available MIDI input port
input_port_name = input_ports[0]
with mido.open_input(input_port_name) as input_port:
    print(f"Listening on {input_port_name}...")

    # Continuously read and print MIDI messages
    isChannelMuted = [
        True,
        True,
        True,
        True,
        True,
        True
    ]

    channelVolumeLevels = [
        0,
        0,
        0,
        0,
        0,
        0
    ]

    micLive = [
        False,
        False,
        False,
        False,
        False,
        False
    ]
    for message in input_port:
        if message.control == 27 and message.value == 1: #Mute button
            isChannelMuted[message.channel] = not isChannelMuted[message.channel]

            if channelVolumeLevels[message.channel] > 1:
                micLive[message.channel] = not isChannelMuted[message.channel]


        if message.control == 15: #volume change
            channelVolumeLevels[message.channel] = message.value

            if message.value > 1:
                micLive[message.channel] = not isChannelMuted[message.channel]
            else:
                micLive[message.channel] = False
    
        debug()
